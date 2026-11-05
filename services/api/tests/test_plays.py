"""apply_play: once per play, with win probability; a looped replay starts over."""
from app import apply_play


def _p(seq, home, away, clock="5:00", wall="2026-11-05T00:00:00Z"):
    return {"game_id": "1", "seq": seq, "period": 4, "clock": clock,
            "home_score": home, "away_score": away, "wallclock": wall}


def test_play_added_once_with_win_probability():
    store = {}
    assert apply_play(store, _p(0, 90, 80))
    assert not apply_play(store, _p(0, 90, 80))
    assert store["1"][0]["home_wp"] > 0.9


def test_replay_loop_resets_game():
    store = {}
    apply_play(store, _p(0, 0, 0, wall="2026-11-05T00:00:00Z"))
    apply_play(store, _p(1, 2, 0))
    assert apply_play(store, _p(0, 0, 0, wall="2026-11-05T09:00:00Z"))   # different wallclock = new run
    assert list(store["1"]) == [0]
