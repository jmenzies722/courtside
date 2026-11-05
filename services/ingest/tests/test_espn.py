"""ESPN adapter tests. No real network: a fake transport plays ESPN."""
import httpx
import pytest

import espn


def _game(gid, home_score="98", away_score="95"):
    """Build one fake ESPN game in ESPN's shape."""
    return {
        "id": gid,
        "status": {"type": {"state": "in"}, "period": 4, "displayClock": "2:31"},
        "competitions": [{"competitors": [
            {"homeAway": "home", "team": {"abbreviation": "NY"}, "score": home_score},
            {"homeAway": "away", "team": {"abbreviation": "CHI"}, "score": away_score},
        ]}],
    }


def _client(payload, status=200):
    """An httpx client whose 'server' always returns this payload."""
    return httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(status, json=payload)))


def test_good_game_is_parsed():
    games = espn.fetch_games(_client({"events": [_game("1")]}))
    assert games[0].home == "NY"
    assert games[0].home_score == 98          # text "98" became the number 98


def test_bad_score_is_skipped_not_fatal():
    feed = {"events": [_game("1"), _game("2", home_score="N/A"), _game("3")]}
    games = espn.fetch_games(_client(feed))
    assert [g.game_id for g in games] == ["1", "3"]


def test_missing_score_before_tipoff_is_zero():
    games = espn.fetch_games(_client({"events": [_game("1", None, None)]}))
    assert games[0].home_score == 0


def test_every_game_bad_means_source_is_broken():
    feed = {"events": [_game(str(i), home_score="N/A") for i in range(14)]}
    with pytest.raises(espn.SourceError, match="format change"):
        espn.fetch_games(_client(feed))


def test_no_games_tonight_is_fine():
    assert espn.fetch_games(_client({"events": []})) == []


def test_source_down_raises_source_error():
    with pytest.raises(espn.SourceError):
        espn.fetch_games(_client({}, status=503))
