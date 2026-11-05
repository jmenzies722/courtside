"""Win probability from score margin and time left (the classic Stern 1994 model).

Idea: treat the rest of the game as random scoring "noise". The final margin is
today's margin + home advantage still to come + noise, and the noise shrinks as
the clock runs down. So a 5-point lead with 10 minutes left is shaky; with 10
seconds left it's nearly certain.

  P(home wins) = Phi( (margin + HOME_EDGE * f) / (SIGMA * sqrt(f)) )
  f = fraction of the game still to play,  Phi = normal distribution CDF

Plain math, not AI: fast, explainable, and testable. (Design rule from the plan.)
"""
import math

GAME_SECONDS = 48 * 60
SIGMA = 13.5        # std dev of an NBA final margin, in points
HOME_EDGE = 2.5     # home teams win by ~2.5 points on average


def seconds_left(period: int, clock: str) -> float:
    """Game seconds remaining. Clock is "M:SS" or "SS.s" (under a minute)."""
    if ":" in clock:
        m, s = clock.split(":")
        in_period = int(m) * 60 + float(s)
    else:
        in_period = float(clock or 0)
    if period > 4:                      # overtime: only this 5-minute period is left
        return in_period
    return (4 - period) * 720 + in_period


def home_win_probability(home: int, away: int, period: int, clock: str) -> float:
    margin = home - away
    f = seconds_left(period, clock) / GAME_SECONDS
    if f <= 0:
        return 1.0 if margin > 0 else 0.0 if margin < 0 else 0.5   # tied at 0:00 = overtime coin flip
    z = (margin + HOME_EDGE * f) / (SIGMA * math.sqrt(f))
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))                   # Phi(z)
