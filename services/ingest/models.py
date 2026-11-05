"""The GameEvent contract: the one data shape every Courtside service agrees on."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GameEvent(BaseModel):
    """One snapshot of one game at one moment."""

    game_id: str
    home: str = Field(min_length=2, max_length=4)   # team code, e.g. "NY"
    away: str = Field(min_length=2, max_length=4)
    home_score: int = Field(ge=0)                   # ge=0: never negative
    away_score: int = Field(ge=0)
    status: Literal["pre", "in", "post"]            # not started, live, final
    period: int = Field(ge=0)                       # quarter (5+ = overtime)
    clock: str                                      # e.g. "2:31"
    fetched_at: datetime                            # when WE fetched it: the freshness SLO clock
    replay_of: str | None = None                    # YYYYMMDD if this is a recorded game played back, else live


class Play(BaseModel):
    """One real play from a game's play-by-play (the score is AFTER the play)."""

    game_id: str
    seq: int = Field(ge=0)                          # order within the game
    period: int = Field(ge=1)
    clock: str
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)
    team: str | None                                # team code, None for game events ("End of Game")
    scoring: bool
    points: int = Field(ge=0)
    text: str                                       # e.g. "Cade Cunningham makes 13-foot pullup jump shot"
    wallclock: datetime                             # real-world time the play happened


class GameRecording(BaseModel):
    """A whole real game, saved once so it can be replayed any time."""

    game_id: str
    home: str
    away: str
    plays: list[Play]
