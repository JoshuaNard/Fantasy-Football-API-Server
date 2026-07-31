from web_scraping.base import FetchedPayload
from web_scraping.sources import ADAPTERS
from web_scraping.sources.kalshi import KalshiAdapter


def _market(player, line, bid, ask):
    return {
        "yes_sub_title": player,
        "floor_strike": line,
        "yes_bid_dollars": str(bid),
        "yes_ask_dollars": str(ask),
    }


KALSHI_PAYLOAD = {
    "series": {
        "KXNFLSEASONRECYDS": {
            "events": [
                {
                    "markets": [
                        _market("A.J. Brown", 999.5, 0.7, 0.8),
                        _market("A.J. Brown", 1199.5, 0.2, 0.3),
                    ]
                }
            ]
        },
        "KXNFLSEASONREC": {
            "events": [
                {
                    "markets": [
                        _market("A.J. Brown", 79.5, 0.45, 0.55),
                    ]
                }
            ]
        },
    }
}


def test_kalshi_is_registered():
    assert ADAPTERS["kalshi"] is KalshiAdapter


def test_fetch_collects_every_configured_public_series(monkeypatch):
    urls = []

    def fake_fetch_json(url, timeout):
        urls.append((url, timeout))
        return FetchedPayload(url, 200, "application/json", {}, {"events": []})

    monkeypatch.setattr(KalshiAdapter, "fetch_json", staticmethod(fake_fetch_json))

    result = KalshiAdapter().fetch(timeout=14)

    assert len(result.payload["series"]) == 6
    assert len(urls) == 6
    assert all("status=open" in url for url, _timeout in urls)
    assert all(timeout == 14 for _url, timeout in urls)


def test_players_calculates_market_implied_stat_estimates():
    players = KalshiAdapter().players(KALSHI_PAYLOAD)

    assert len(players) == 1
    assert players[0].full_name == "A.J. Brown"
    assert players[0].attributes["estimate_type"] == "market_implied_median"
    assert players[0].attributes["projections"] == {
        "receiving_yards": 1099.5,
        "receptions": 79.5,
    }


def test_players_rejects_non_mapping_payload():
    assert not KalshiAdapter().players("not JSON")
