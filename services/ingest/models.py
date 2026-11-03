from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class GameEvent(BaseModel):
    """One snapshot of one game. The contract every service relies on."""
    game_id: str
    home: str = Field(min_length=2, max_length=4)   # team code, e.g. "NY"
    away: str = Field(min_length=2, max_length=4)
    home_score: int = Field(ge=0)                   # never negative
    away_score: int = Field(ge=0)
    status: Literal["pre", "in", "post"]            # not started, live, final
    period: int = Field(ge=0)
    clock: str
    fetched_at: datetime                            # when WE fetched it: key for the freshness SLO
