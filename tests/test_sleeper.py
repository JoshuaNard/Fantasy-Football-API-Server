from web_scraping.base import FetchedPayload
from web_scraping.sources import ADAPTERS
from web_scraping.sources.sleeper import SleeperAdapter


def test_sleeper_is_registered():
    assert ADAPTERS["sleeper"] is SleeperAdapter


def test_fetch_uses_sleeper_player_endpoint(monkeypatch):
    expected = FetchedPayload(
        url=SleeperAdapter.players_url,
        status=200,
        content_type="application/json",
        headers={},
        payload={},
    )
    called = {}

    def fake_fetch_json(url, timeout):
        called.update(url=url, timeout=timeout)
        return expected

    monkeypatch.setattr(SleeperAdapter, "fetch_json", staticmethod(fake_fetch_json))

    assert SleeperAdapter().fetch(timeout=17) is expected
    assert called == {"url": SleeperAdapter.players_url, "timeout": 17}


def test_players_normalizes_records_and_preserves_all_source_attributes():
    payload = {
        "4046": {
            "full_name": "Patrick Mahomes",
            "first_name": "Patrick",
            "last_name": "Mahomes",
            "position": "QB",
            "team": "KC",
            "active": True,
            "fantasy_positions": ["QB"],
            "years_exp": 9,
        },
        "9999": {
            "first_name": "Retired",
            "last_name": "Player",
            "position": "WR",
            "active": False,
        },
        "invalid": "not a player object",
        "unnamed": {"position": "RB"},
    }

    records = SleeperAdapter().players(payload)

    assert len(records) == 2
    assert records[0].external_id == "4046"
    assert records[0].full_name == "Patrick Mahomes"
    assert records[0].position == "QB"
    assert records[0].team == "KC"
    assert records[0].attributes is payload["4046"]
    assert records[0].attributes["fantasy_positions"] == ["QB"]
    assert records[1].full_name == "Retired Player"
    assert records[1].active is False


def test_players_does_not_mutate_the_raw_payload():
    payload = {
        "1": {
            "full_name": "Example Player",
            "position": "RB",
            "custom_field": {"nested": True},
        }
    }
    original = payload["1"].copy()

    SleeperAdapter().players(payload)

    assert payload["1"] == original
