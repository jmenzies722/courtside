"""Replay mode: real past games, played back at real speed.

  record:  python replay.py record 20261104      saves every game that night to local/replays/20261104/
  replay:  SOURCE=replay REPLAY_DATE=20261104    the worker emits those games as if they were live

Every game tips off together when the replay starts, then follows its REAL play timing
(the gaps between ESPN's play timestamps). REPLAY_SPEED=10 runs ten times faster.
"""
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

from espn import fetch_recording, list_game_ids
from models import GameEvent, GameRecording, Play

REPLAY_ROOT = Path(__file__).resolve().parents[2] / "local" / "replays"
RESTART_AFTER_SECONDS = 60      # once every game is final, wait this long, then start again


class ReplayFeed:
    def __init__(self, date: str, speed: float = 1.0, clock=time.monotonic):
        files = sorted((REPLAY_ROOT / date).glob("*.json"))
        if not files:
            raise SystemExit(f"no recordings in {REPLAY_ROOT / date}: run  make record DATE={date}")
        self.games = [GameRecording.model_validate_json(f.read_text()) for f in files]
        # seconds from tip-off for every play, from the real timestamps
        self.offsets = [[(p.wallclock - g.plays[0].wallclock).total_seconds() for p in g.plays]
                        for g in self.games]
        self.speed, self.clock, self.started = speed, clock, clock()
        self.reached = [0] * len(self.games)   # newest play index each game has reached
        self.sent = [-1] * len(self.games)     # newest play index already handed out

    def _elapsed(self) -> float:
        elapsed = (self.clock() - self.started) * self.speed
        longest = max(o[-1] for o in self.offsets)
        if elapsed > longest + RESTART_AFTER_SECONDS * self.speed:   # whole slate finished: loop
            self.started = self.clock()
            elapsed = 0.0
        return elapsed

    def fetch(self) -> list[GameEvent]:
        elapsed, now, events = self._elapsed(), datetime.now(timezone.utc), []
        for game, offsets in zip(self.games, self.offsets):
            i = max(k for k, t in enumerate(offsets) if t <= elapsed)   # newest play that has "happened"
            self.reached[self.games.index(game)] = i
            play, done = game.plays[i], i == len(game.plays) - 1
            events.append(GameEvent(
                game_id=game.game_id, home=game.home, away=game.away,
                home_score=play.home_score, away_score=play.away_score,
                status="post" if done else "in", period=play.period, clock=play.clock,
                fetched_at=now,
            ))
        return events

    def new_plays(self) -> list[Play]:
        """Plays that happened since the last call (call after fetch())."""
        plays: list[Play] = []
        for n, game in enumerate(self.games):
            if self.reached[n] < self.sent[n]:       # the slate looped: start this game over
                self.sent[n] = -1
            plays += game.plays[self.sent[n] + 1 : self.reached[n] + 1]
            self.sent[n] = self.reached[n]
        return plays


def record(date: str) -> None:
    out = REPLAY_ROOT / date
    out.mkdir(parents=True, exist_ok=True)
    with httpx.Client() as client:
        for gid in list_game_ids(client, date):
            rec = fetch_recording(client, gid)
            (out / f"{gid}.json").write_text(rec.model_dump_json())
            print(f"saved {rec.away} @ {rec.home}: {len(rec.plays)} plays")


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] != "record":
        raise SystemExit("usage: python replay.py record YYYYMMDD")
    record(sys.argv[2])
