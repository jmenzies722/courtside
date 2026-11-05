"""ESPN adapter: the ONLY file that knows ESPN's format.

Swap this file for another provider later; nothing else changes.
"""
import logging
from datetime import datetime, timezone

import httpx
from pydantic import ValidationError

from models import GameEvent, GameRecording, Play

log = logging.getLogger("ingest.espn")

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
SUMMARY_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"
TIMEOUT_SECONDS = 5.0  # never wait forever on someone else's server


class SourceError(Exception):
    """The source itself failed: down, slow, blocked, or not JSON."""


def fetch_games(client: httpx.Client) -> list[GameEvent]:
    """Fetch the scoreboard. Bad games are skipped; a bad source raises SourceError."""
    try:
        resp = client.get(SCOREBOARD_URL, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()          # turn 4xx/5xx into an exception
        data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise SourceError(f"ESPN fetch failed: {exc}") from exc

    fetched_at = datetime.now(timezone.utc)
    games: list[GameEvent] = []
    for raw in data.get("events", []):
        try:
            games.append(_parse(raw, fetched_at))
        except (KeyError, IndexError, ValidationError) as exc:
            # one broken game must not sink the rest (small blast radius)
            log.warning("skipping game %s: %s", raw.get("id", "?"), exc)
            continue

    raw_count = len(data.get("events", []))
    if raw_count and not games:
        # every game failed: that's not bad luck, the source format changed
        raise SourceError(f"all {raw_count} games failed to parse: format change?")
    return games


def _parse(raw: dict, fetched_at: datetime) -> GameEvent:
    """Translate one ESPN game into our GameEvent contract."""
    comp = raw["competitions"][0]
    teams = {c["homeAway"]: c for c in comp["competitors"]}
    status = raw["status"]
    return GameEvent(
        game_id=raw["id"],
        home=teams["home"]["team"]["abbreviation"],
        away=teams["away"]["team"]["abbreviation"],
        home_score=teams["home"].get("score") or 0,   # missing before tip-off -> 0
        away_score=teams["away"].get("score") or 0,   # pydantic turns "98" into 98, rejects "N/A"
        status=status["type"]["state"],
        period=status.get("period", 0),
        clock=status.get("displayClock", ""),
        fetched_at=fetched_at,
    )


def _get_json(client: httpx.Client, url: str, **params) -> dict:
    try:
        resp = client.get(url, params=params, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise SourceError(f"ESPN fetch failed: {exc}") from exc


def list_game_ids(client: httpx.Client, date: str) -> list[str]:
    """IDs of every game on a date (YYYYMMDD)."""
    return [e["id"] for e in _get_json(client, SCOREBOARD_URL, dates=date).get("events", [])]


def fetch_recording(client: httpx.Client, game_id: str) -> GameRecording:
    """One game's full play-by-play, translated into our Play contract."""
    data = _get_json(client, SUMMARY_URL, event=game_id)
    teams = {c["team"]["id"]: c for c in data["header"]["competitions"][0]["competitors"]}
    side = {c["homeAway"]: c["team"]["abbreviation"] for c in teams.values()}
    plays: list[Play] = []
    for raw in data.get("plays", []):
        try:
            team_id = (raw.get("team") or {}).get("id")
            plays.append(Play(
                game_id=game_id, seq=len(plays), period=raw["period"]["number"],
                clock=raw["clock"]["displayValue"],
                home_score=raw["homeScore"], away_score=raw["awayScore"],
                team=teams[team_id]["team"]["abbreviation"] if team_id in teams else None,
                scoring=bool(raw.get("scoringPlay")), points=raw.get("scoreValue") or 0,
                text=raw.get("text", ""), wallclock=raw["wallclock"],
            ))
        except (KeyError, ValidationError) as exc:
            log.warning("skipping play in game %s: %s", game_id, exc)   # same rule: one bad play, not the game
    if not plays:
        raise SourceError(f"game {game_id} has no usable plays")
    return GameRecording(game_id=game_id, home=side["home"], away=side["away"], plays=plays)
