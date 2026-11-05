"""Replay must follow real play timing, finish games, and loop the slate."""
import json

import httpx

import espn
import replay
from models import GameRecording, Play


def _play(seq, secs, home, away):
    return Play(game_id="g1", seq=seq, period=1, clock="12:00", home_score=home, away_score=away,
                team="NY", scoring=True, points=2, text="shot",
                wallclock=f"2026-11-05T00:00:{secs:02d}Z")


def _feed(tmp_path, monkeypatch, plays, speed=1.0):
    day = tmp_path / "20261104"
    day.mkdir()
    rec = GameRecording(game_id="g1", home="NY", away="BOS", plays=plays)
    (day / "g1.json").write_text(rec.model_dump_json())
    monkeypatch.setattr(replay, "REPLAY_ROOT", tmp_path)
    now = {"t": 0.0}
    return replay.ReplayFeed("20261104", speed, clock=lambda: now["t"]), now


def test_replay_follows_real_timing(tmp_path, monkeypatch):
    feed, now = _feed(tmp_path, monkeypatch, [_play(0, 0, 0, 0), _play(1, 10, 2, 0), _play(2, 30, 2, 3)])
    assert feed.fetch()[0].home_score == 0          # tip-off
    now["t"] = 12
    assert feed.fetch()[0].home_score == 2          # the play at +10s has happened, +30s hasn't
    now["t"] = 31
    game = feed.fetch()[0]
    assert (game.away_score, game.status) == (3, "post")


def test_speed_and_loop(tmp_path, monkeypatch):
    feed, now = _feed(tmp_path, monkeypatch, [_play(0, 0, 0, 0), _play(1, 30, 2, 0)], speed=10)
    now["t"] = 3                                     # 3s x10 = 30s of game time
    assert feed.fetch()[0].status == "post"
    now["t"] = 100                                   # well past the restart wait: slate loops
    assert feed.fetch()[0].home_score == 0


def test_fetch_recording_translates_espn_plays():
    summary = {
        "header": {"competitions": [{"competitors": [
            {"homeAway": "home", "team": {"id": "8", "abbreviation": "DET"}},
            {"homeAway": "away", "team": {"id": "20", "abbreviation": "PHI"}}]}]},
        "plays": [
            {"period": {"number": 1}, "clock": {"displayValue": "10:50"}, "homeScore": 2, "awayScore": 0,
             "team": {"id": "8"}, "scoringPlay": True, "scoreValue": 2, "text": "Cunningham layup",
             "wallclock": "2026-11-05T00:14:24Z"},
            {"period": {"number": 1}},                                   # broken play: skipped
        ],
    }
    client = httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(200, json=summary)))
    rec = espn.fetch_recording(client, "1")
    assert (rec.home, rec.away, len(rec.plays)) == ("DET", "PHI", 1)
    assert rec.plays[0].team == "DET" and rec.plays[0].scoring


def test_new_plays_hands_out_each_play_once(tmp_path, monkeypatch):
    feed, now = _feed(tmp_path, monkeypatch, [_play(0, 0, 0, 0), _play(1, 10, 2, 0), _play(2, 30, 2, 3)])
    feed.fetch()
    assert [p.seq for p in feed.new_plays()] == [0]
    now["t"] = 12
    feed.fetch()
    assert [p.seq for p in feed.new_plays()] == [1]
    feed.fetch()
    assert feed.new_plays() == []                    # nothing new: nothing re-sent
