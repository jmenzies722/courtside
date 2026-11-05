"""Backoff tests: wait longer after each failure, but never more than the cap."""
import worker


def test_backoff_grows_then_caps():
    assert [worker.next_delay(n) for n in range(5)] == [10, 20, 40, 60, 60]
