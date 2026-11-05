"""API: reads game events from the queue, keeps the newest per game, streams changes to the page.

Walking-skeleton shortcut: this service reads the queue directly. In L4 a separate
stats service takes over that job and this API reads from Redis instead.
"""
import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

import boto3

from winprob import home_win_probability, seconds_left
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

QUEUE_NAME = os.getenv("QUEUE_NAME", "game-events")
PLAY_QUEUE_NAME = os.getenv("PLAY_QUEUE_NAME", "play-events")
SQS_ENDPOINT_URL = os.getenv("SQS_ENDPOINT_URL")

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("api")

games: dict[str, dict] = {}   # game_id -> newest snapshot (in memory for now; Redis in L4)
plays: dict[str, dict[int, dict]] = {}   # game_id -> {seq: play}
state = {"version": 0}        # bumps on every scoreboard change, so streams know when to send
game_versions: dict[str, int] = {}       # per-game change counter for game-page streams


def apply(store: dict[str, dict], event: dict) -> bool:
    """Keep only the newest snapshot per game. Returns True if anything changed.

    Idempotent: the same message twice (SQS is at-least-once) changes nothing.
    An older snapshot arriving late is ignored.
    """
    current = store.get(event["game_id"])
    if current and datetime.fromisoformat(current["fetched_at"]) >= datetime.fromisoformat(event["fetched_at"]):
        return False
    store[event["game_id"]] = event
    return True


def apply_play(store: dict[str, dict[int, dict]], play: dict) -> bool:
    """Add one play, with its win probability. Duplicates change nothing.

    A seq-0 play for a game we already have means the replay looped: start that game over.
    """
    game_plays = store.setdefault(play["game_id"], {})
    if play["seq"] == 0 and game_plays and 0 in game_plays and play["wallclock"] != game_plays[0]["wallclock"]:
        game_plays.clear()
    if play["seq"] in game_plays:
        return False
    play["home_wp"] = round(home_win_probability(
        play["home_score"], play["away_score"], play["period"], play["clock"]), 4)
    game_plays[play["seq"]] = play
    return True


def _with_wp(game: dict) -> dict:
    """Scoreboard row + current home win probability."""
    return {**game, "home_wp": round(home_win_probability(
        game["home_score"], game["away_score"], max(game["period"], 1), game["clock"] or "12:00"), 4)}


def _sqs():
    if SQS_ENDPOINT_URL:   # local stand-in: fake credentials so it can never reach real AWS
        return boto3.client("sqs", endpoint_url=SQS_ENDPOINT_URL, region_name="us-east-1",
                            aws_access_key_id="local", aws_secret_access_key="local")
    return boto3.client("sqs")


def _receive_batch(sqs, url, kind: str) -> int:
    """One long-poll: wait up to 5s for up to 10 messages, apply them, then delete them."""
    msgs = sqs.receive_message(QueueUrl=url, MaxNumberOfMessages=10, WaitTimeSeconds=5).get("Messages", [])
    changed = 0
    for m in msgs:
        event = json.loads(m["Body"])
        if kind == "play":
            if apply_play(plays, event):
                game_versions[event["game_id"]] = game_versions.get(event["game_id"], 0) + 1
                changed += 1
        elif apply(games, event):
            game_versions[event["game_id"]] = game_versions.get(event["game_id"], 0) + 1
            changed += 1
    if msgs:   # delete only AFTER applying: if we crash first, the messages come back (at-least-once)
        sqs.delete_message_batch(QueueUrl=url, Entries=[
            {"Id": str(i), "ReceiptHandle": m["ReceiptHandle"]} for i, m in enumerate(msgs)])
    return changed


async def consume(queue_name: str, kind: str) -> None:
    """Background loop: read one queue forever. Queue down? Log, wait, retry; never crash the API."""
    failures = 0
    while True:
        try:
            sqs = _sqs()
            url = sqs.get_queue_url(QueueName=queue_name)["QueueUrl"]
            log.info(json.dumps({"msg": "consuming", "queue": url}))
            failures = 0
            while True:
                if await asyncio.to_thread(_receive_batch, sqs, url, kind):   # boto3 blocks, so use a thread
                    state["version"] += 1
        except asyncio.CancelledError:
            raise
        except Exception as exc:   # queue unreachable, bad message, etc.
            failures += 1
            wait = min(2 ** failures, 30)
            log.warning(json.dumps({"msg": "queue error", "retry_in": wait, "error": str(exc)[:120]}))
            await asyncio.sleep(wait)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    tasks = [asyncio.create_task(consume(QUEUE_NAME, "game")),      # start reading both queues
             asyncio.create_task(consume(PLAY_QUEUE_NAME, "play"))]
    yield
    for t in tasks:
        t.cancel()                                                  # and stop cleanly on shutdown


app = FastAPI(title="Courtside API", lifespan=lifespan)


@app.get("/healthz")
def healthz():
    """Liveness check: Kubernetes probes this in L4."""
    return {"ok": True, "games": len(games)}


@app.get("/api/games")
def list_games():
    return [_with_wp(g) for g in sorted(games.values(), key=lambda g: g["game_id"])]


def game_detail(game_id: str) -> dict:
    if game_id not in games:
        raise HTTPException(404, "game not found")
    ordered = sorted(plays.get(game_id, {}).values(), key=lambda p: p["seq"])
    return {
        "game": _with_wp(games[game_id]),
        "plays": ordered[-60:][::-1],                                 # newest first, last 60
        "wp": [{"seq": p["seq"], "t": 2880 - _left(p), "home_wp": p["home_wp"]} for p in ordered],
    }


def _left(p: dict) -> float:
    """Seconds left in regulation (overtime plots at the end of the chart)."""
    return seconds_left(p["period"], p["clock"]) if p["period"] <= 4 else 0.0


@app.get("/api/games/{game_id}")
def get_game(game_id: str):
    return game_detail(game_id)


@app.get("/api/games/{game_id}/stream")
async def game_stream(game_id: str):
    """SSE for one game: pushes plays + win probability whenever this game changes."""
    game_detail(game_id)   # 404 now, before opening a stream

    async def events():
        seen = -1
        while True:
            v = game_versions.get(game_id, 0)
            if v != seen:
                seen = v
                yield f"data: {json.dumps(game_detail(game_id))}\n\n"
            else:
                yield ": keep-alive\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(events(), media_type="text/event-stream")


@app.get("/api/stream")
async def stream():
    """Server-Sent Events: one open connection; we push the scoreboard whenever it changes."""
    async def events():
        seen = -1
        while True:
            if state["version"] != seen:
                seen = state["version"]
                yield f"data: {json.dumps(list_games())}\n\n"
            else:
                yield ": keep-alive\n\n"   # comment line: keeps proxies from closing an idle stream
            await asyncio.sleep(1)
    return StreamingResponse(events(), media_type="text/event-stream")

