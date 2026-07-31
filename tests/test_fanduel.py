from web_scraping.base import FetchedPayload
from web_scraping.sources import ADAPTERS
from web_scraping.sources.fanduel import FanDuelAdapter


FANDUEL_PAYLOAD = {
    "attachments": {
        "markets": {
            "one": {
                "marketName": "A.J. Brown Regular Season Receiving Yards 2026-27",
                "runners": [
                    {
                        "runnerName": "A.J. Brown Over 1099.5",
                        "runnerStatus": "ACTIVE",
                    },
                    {
                        "runnerName": "A.J. Brown Under 1099.5",
                        "runnerStatus": "ACTIVE",
                    },
                ],
            },
            "two": {
                "marketName": "A.J. Brown Regular Season Receiving TDs 2026-27",
                "runners": [
                    {
                        "runnerName": "A.J. Brown Over 7.5",
                        "runnerStatus": "ACTIVE",
                    }
                ],
            },
            "unrelated": {
                "marketName": "A.J. Brown MVP 2026-27",
                "runners": [],
            },
        }
    }
}


def test_fanduel_is_registered():
    assert ADAPTERS["fanduel"] is FanDuelAdapter


def test_fetch_uses_anonymous_nfl_page(monkeypatch):
    expected = FetchedPayload(
        FanDuelAdapter.projections_url,
        200,
        "application/json",
        {},
        FANDUEL_PAYLOAD,
    )
    called = {}

    def fake_fetch_json(url, timeout):
        called.update(url=url, timeout=timeout)
        return expected

    monkeypatch.setattr(FanDuelAdapter, "fetch_json", staticmethod(fake_fetch_json))

    assert FanDuelAdapter().fetch(timeout=11) is expected
    assert called == {"url": FanDuelAdapter.projections_url, "timeout": 11}


def test_players_aggregates_every_supported_regular_season_stat():
    players = FanDuelAdapter().players(FANDUEL_PAYLOAD)

    assert len(players) == 1
    assert players[0].full_name == "A.J. Brown"
    assert players[0].attributes["projections"] == {
        "receiving_yards": 1099.5,
        "receiving_touchdowns": 7.5,
    }


def test_players_rejects_non_mapping_payload():
    assert not FanDuelAdapter().players("not JSON")
