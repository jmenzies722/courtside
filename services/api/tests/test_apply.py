"""apply() must be idempotent and ignore late, older snapshots."""
from app import apply


def _ev(score, at):
    return {"game_id": "1", "home_score": score, "fetched_at": at}


def test_newer_snapshot_wins():
    store = {}
    assert apply(store, _ev(10, "2026-11-05T20:00:00Z"))
    assert apply(store, _ev(12, "2026-11-05T20:00:10Z"))
    assert store["1"]["home_score"] == 12


def test_duplicate_changes_nothing():
    store = {}
    apply(store, _ev(10, "2026-11-05T20:00:00Z"))
    assert not apply(store, _ev(10, "2026-11-05T20:00:00Z"))


def test_late_older_snapshot_is_ignored():
    store = {}
    apply(store, _ev(12, "2026-11-05T20:00:10Z"))
    assert not apply(store, _ev(10, "2026-11-05T20:00:00Z"))
    assert store["1"]["home_score"] == 12
