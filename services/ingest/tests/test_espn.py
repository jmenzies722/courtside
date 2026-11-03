"""Regression tests: one bad game must never take down the batch."""
import httpx

import espn


def _game(gid, home_score, away_score="95"):
    return {
        "id": gid,
        "status": {"type": {"state": "in"}, "period": 4, "displayClock": "2:31"},
        "competitions": [{"competitors": [
            {"homeAway": "home", "team": {"abbreviation": "NY"}, "score": home_score},
            {"homeAway": "away", "team": {"abbreviation": "CHI"}, "score": away_score},
        ]}],
    }


def _client(payload, status=200):
    return httpx.Client(transport=httpx.MockTransport(
        lambda req: httpx.Response(status, json=payload)))


def test_bad_score_is_skipped_not_fatal():
    feed = {"events": [_game("1", "98"), _game("2", "N/A"), _game("3", "101")]}
    games = espn.fetch_games(_client(feed))
    assert [g.game_id for g in games] == ["1", "3"]
    assert games[0].home_score == 98            # "98" text became the number 98


def test_missing_score_before_tipoff_is_zero():
    games = espn.fetch_games(_client({"events": [_game("1", None, None)]}))
    assert games[0].home_score == 0


def test_source_down_raises_source_error():
    try:
        espn.fetch_games(_client({}, status=503))
        assert False, "should have raised"
    except espn.SourceError:
        pass
