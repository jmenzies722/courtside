"""ESPN source adapter: the ONLY file that knows ESPN's format.
Swap this file for a licensed provider later; nothing else changes."""
import logging
from datetime import datetime, timezone

import httpx
from pydantic import ValidationError

from models import GameEvent

log = logging.getLogger("ingest.espn")

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
TIMEOUT_SECONDS = 5.0  # never wait forever on someone else's server


class SourceError(Exception):
    """The source itself failed (down, blocked, slow, garbage)."""


def fetch_games(client: httpx.Client) -> list[GameEvent]:
    try:
        resp = client.get(SCOREBOARD_URL, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise SourceError(f"ESPN fetch failed: {exc}") from exc

    fetched_at = datetime.now(timezone.utc)
    games: list[GameEvent] = []
    for raw in data.get("events", []):
        try:
            games.append(_parse(raw, fetched_at))
        except (KeyError, IndexError, ValidationError) as exc:
            # one broken game must not sink the other 13
            log.warning("skipping game %s: %s", raw.get("id", "?"), exc)
    return games


def _parse(raw: dict, fetched_at: datetime) -> GameEvent:
    comp = raw["competitions"][0]
    teams = {c["homeAway"]: c for c in comp["competitors"]}
    status = raw["status"]
    return GameEvent(
        game_id=raw["id"],
        home=teams["home"]["team"]["abbreviation"],
        away=teams["away"]["team"]["abbreviation"],
        home_score=teams["home"].get("score") or 0,   # pydantic converts "98" -> 98, rejects "N/A"
        away_score=teams["away"].get("score") or 0,
        status=status["type"]["state"],
        period=status.get("period", 0),
        clock=status.get("displayClock", ""),
        fetched_at=fetched_at,
    )
