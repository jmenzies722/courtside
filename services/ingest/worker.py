"""Ingest worker: poll the source, emit GameEvents, back off on failure, stop cleanly."""
import json
import logging
import os
import signal
import threading

import httpx

from espn import SourceError, fetch_games

POLL_SECONDS = float(os.getenv("POLL_SECONDS", "10"))   # normal pace
MAX_BACKOFF_SECONDS = 60.0                              # never wait longer than this

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("ingest")
stop = threading.Event()


def next_delay(failures: int) -> float:
    """0 failures -> 10s; then 20, 40, capped at 60."""
    if failures == 0:
        return POLL_SECONDS
    return min(POLL_SECONDS * 2 ** failures, MAX_BACKOFF_SECONDS)


def _handle_stop(signum, _frame):
    log.info(json.dumps({"msg": "shutdown requested", "signal": signal.Signals(signum).name}))
    stop.set()


def emit(event) -> None:
    # Step 4: print one JSON line per game. Later this becomes "send to SQS".
    print(event.model_dump_json(), flush=True)


def run() -> None:
    signal.signal(signal.SIGTERM, _handle_stop)   # how Kubernetes says "please stop"
    signal.signal(signal.SIGINT, _handle_stop)    # Ctrl-C
    failures = 0
    log.info(json.dumps({"msg": "worker started", "poll_seconds": POLL_SECONDS}))
    with httpx.Client() as client:
        while not stop.is_set():
            try:
                games = fetch_games(client)
                for g in games:
                    emit(g)
                failures = 0
                log.info(json.dumps({"msg": "poll ok", "games": len(games)}))
            except SourceError as exc:
                failures += 1
                log.warning(json.dumps({"msg": "poll failed", "failures": failures,
                                        "retry_in": next_delay(failures), "error": str(exc)[:120]}))
            stop.wait(next_delay(failures))   # sleeps, but wakes instantly on shutdown
    log.info(json.dumps({"msg": "worker stopped cleanly"}))


if __name__ == "__main__":
    run()
