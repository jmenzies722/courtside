"""Backoff tests: wait longer after each failure, but never more than the cap."""
import worker


def test_backoff_grows_then_caps():
    assert [worker.next_delay(n) for n in range(5)] == [10, 20, 40, 60, 60]


def test_queue_down_does_not_crash_worker(monkeypatch):
    """Regression (L3-1 break-it): a queue outage must back off, not kill the worker."""
    from botocore.exceptions import EndpointConnectionError

    calls = {"n": 0}

    def queue_down(*_args):
        calls["n"] += 1
        if calls["n"] >= 2:
            worker.stop.set()                      # end the test after the second attempt
        raise EndpointConnectionError(endpoint_url="http://localhost:9324/")

    monkeypatch.setattr(worker, "make_queue", lambda: (object(), {"game": "g", "play": "p"}))
    monkeypatch.setattr(worker, "fetch_games", lambda client: [])
    monkeypatch.setattr(worker, "live_new_plays", lambda *a: [])
    monkeypatch.setattr(worker, "emit", queue_down)
    monkeypatch.setattr(worker, "next_delay", lambda failures: 0)
    monkeypatch.setattr(worker.signal, "signal", lambda *a: None)
    worker.stop.clear()
    worker.run()                                   # before the fix, this raised
    assert calls["n"] == 2                         # it retried instead of dying
