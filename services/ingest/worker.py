"""Ingest worker: poll the source, emit GameEvents, back off on failure, stop cleanly."""
import json
import logging
import os
import signal
import threading

import boto3
import httpx

from espn import SourceError, fetch_games, fetch_recording
from replay import ReplayFeed

SOURCE = os.getenv("SOURCE", "espn")                    # "espn" = live games, "replay" = real past games
POLL_SECONDS = float(os.getenv("POLL_SECONDS", "10"))   # normal pace
MAX_BACKOFF_SECONDS = 60.0                              # never wait longer than this
QUEUE_NAME = os.getenv("QUEUE_NAME")                    # unset = print events instead (no queue)
PLAY_QUEUE_NAME = os.getenv("PLAY_QUEUE_NAME", "play-events")
SQS_ENDPOINT_URL = os.getenv("SQS_ENDPOINT_URL")        # set only for the local stand-in

logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)    # hide httpx's per-request lines (log noise)
log = logging.getLogger("ingest")
stop = threading.Event()   # a flag any thread can raise to say "shut down"


def next_delay(failures: int) -> float:
    """How long to wait before the next poll: 10s normally, then 20, 40, capped at 60."""
    if failures == 0:
        return POLL_SECONDS
    return min(POLL_SECONDS * 2 ** failures, MAX_BACKOFF_SECONDS)


def _handle_stop(signum, _frame):
    log.info(json.dumps({"msg": "shutdown requested", "signal": signal.Signals(signum).name}))
    stop.set()


def make_queue():
    """Return (sqs_client, {"game": url, "play": url}), or (None, {}) to just print events."""
    if not QUEUE_NAME:
        return None, {}
    if SQS_ENDPOINT_URL:
        # Local stand-in: fake credentials on purpose, so this path can never reach real AWS.
        sqs = boto3.client("sqs", endpoint_url=SQS_ENDPOINT_URL, region_name="us-east-1",
                           aws_access_key_id="local", aws_secret_access_key="local")
    else:
        # Real AWS: credentials come from the environment (SSO locally, a pod role in EKS).
        sqs = boto3.client("sqs")
    return sqs, {"game": sqs.get_queue_url(QueueName=QUEUE_NAME)["QueueUrl"],
                 "play": sqs.get_queue_url(QueueName=PLAY_QUEUE_NAME)["QueueUrl"]}


def emit(events, sqs, queue_url) -> None:
    """Send events to the queue in batches of 10 (the SQS max), or print them if there's no queue."""
    bodies = [e.model_dump_json() for e in events]
    if sqs is None:
        for b in bodies:
            print(b, flush=True)
        return
    for start in range(0, len(bodies), 10):   # one request per 10 messages, not one per message
        chunk = bodies[start:start + 10]
        sqs.send_message_batch(QueueUrl=queue_url, Entries=[
            {"Id": str(i), "MessageBody": b} for i, b in enumerate(chunk)])


def live_new_plays(client, games, last_seq: dict) -> list:
    """Live mode: fetch play-by-play for games in progress; keep only plays we haven't sent."""
    plays = []
    for g in games:
        if g.status != "in":
            continue
        rec = fetch_recording(client, g.game_id)
        fresh = [p for p in rec.plays if p.seq > last_seq.get(g.game_id, -1)]
        if fresh:
            last_seq[g.game_id] = fresh[-1].seq
        plays += fresh
    return plays


def run() -> None:
    signal.signal(signal.SIGTERM, _handle_stop)   # how Docker/Kubernetes say "please stop"
    signal.signal(signal.SIGINT, _handle_stop)    # Ctrl-C
    failures = 0
    sqs, urls = make_queue()
    log.info(json.dumps({"msg": "worker started", "source": SOURCE, "poll_seconds": POLL_SECONDS,
                         "queues": urls or "stdout"}))
    last_seq: dict = {}
    replay = (ReplayFeed(os.environ["REPLAY_DATE"], float(os.getenv("REPLAY_SPEED", "1")))
              if SOURCE == "replay" else None)
    with httpx.Client() as client:
        while not stop.is_set():
            try:
                games = replay.fetch() if replay else fetch_games(client)
                plays = replay.new_plays() if replay else live_new_plays(client, games, last_seq)
                emit(plays, sqs, urls.get("play"))     # plays first: the game snapshot summarizes them
                emit(games, sqs, urls.get("game"))
                failures = 0
                log.info(json.dumps({"msg": "poll ok", "games": len(games), "plays": len(plays)}))
            except SourceError as exc:
                failures += 1
                log.warning(json.dumps({"msg": "poll failed", "failures": failures,
                                        "retry_in": next_delay(failures), "error": str(exc)[:120]}))
            stop.wait(next_delay(failures))   # sleeps, but wakes instantly on shutdown
    log.info(json.dumps({"msg": "worker stopped cleanly"}))


if __name__ == "__main__":
    run()
