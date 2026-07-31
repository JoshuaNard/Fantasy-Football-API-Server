"""Tests for DraftKings' NFL projection scraper."""

import json

from web_scraping.base import FetchedPayload
from web_scraping.sources import ADAPTERS
from web_scraping.sources.draftkings import DraftKingsAdapter


PAGE_DATA = {
    "loaderData": {
        "routes/_homeShared": {
            "pickableIdToPickCardMap": {
                "3270611": {
                    "pickCard": {
                        "pickableId": 3270611,
                        "entities": [{"dkId": 913259, "compIds": [6179129]}],
                        "activePickableMarkets": [
                            {
                                "pickableMarketId": 13052114,
                                "pickSixMarketId": 493,
                                "targetValue": 4000.5,
                                "isLive": False,
                                "isPaused": False,
                                "activeSelections": [
                                    {
                                        "pickableMarketSelectionId": 124279628,
                                        "statLinePropositionId": 1,
                                        "standingsMultiplier": 1,
                                    },
                                    {
                                        "pickableMarketSelectionId": 124279629,
                                        "statLinePropositionId": 2,
                                        "standingsMultiplier": 1,
                                    },
                                ],
                            }
                        ],
                    }
                }
            },
            "pickCardLookups": {
                "entityInfoByDkId": {
                    "913259": {
                        "name": "J. Goff",
                        "fullName": "Jared Goff",
                        "jerseyNum": "16",
                    }
                },
                "competitionById": {
                    "6179129": {
                        "name": "2026 Regular Season",
                        "startTime": "2026-09-10T00:20:00+00:00",
                        "entityCompByDkId": {
                            "913259": {"teamId": 1244441}
                        },
                    }
                },
                "displayTeamById": {"1244441": {"name": "DET"}},
                "pickSixMarketById": {
                    "493": {
                        "name": "Passing Yards",
                        "abbreviation": "PaYds",
                        "propositionNameById": {"1": "More", "2": "Less"},
                    }
                },
            },
        }
    }
}


def _flatten_for_test(value):
    """Encode enough React Router flattened JSON for a representative fixture."""
    values = []

    def add(item):
        index = len(values)
        values.append(None)
        if isinstance(item, dict):
            values[index] = {
                f"_{add(key)}": add(child) for key, child in item.items()
            }
        elif isinstance(item, list):
            values[index] = [add(child) for child in item]
        else:
            values[index] = item
        return index

    add(value)
    return values


def _html_fixture():
    stream = json.dumps(_flatten_for_test(PAGE_DATA), separators=(",", ":"))
    encoded = json.dumps(stream)
    return (
        "<html><script>window.__reactRouterContext.streamController."
        f"enqueue({encoded});</script></html>"
    )


def test_draftkings_is_registered():
    assert ADAPTERS["draftkings"] is DraftKingsAdapter


def test_fetch_uses_public_nfl_season_page(monkeypatch):
    expected = FetchedPayload(
        url=DraftKingsAdapter.projections_url,
        status=200,
        content_type="text/html",
        headers={},
        payload=_html_fixture(),
    )
    called = {}

    def fake_fetch_text(url, timeout):
        called.update(url=url, timeout=timeout)
        return expected

    monkeypatch.setattr(DraftKingsAdapter, "fetch_text", staticmethod(fake_fetch_text))

    result = DraftKingsAdapter().fetch(timeout=12)

    assert result.payload["categories"] == []
    assert result.payload["source_page"] == _html_fixture()
    assert called == {"url": DraftKingsAdapter.projections_url, "timeout": 12}


def test_markets_extracts_player_team_line_event_and_both_sides():
    records = DraftKingsAdapter().markets(_html_fixture())

    assert len(records) == 1
    record = records[0]
    assert record.external_id == "13052114"
    assert record.provider == "DraftKings"
    assert record.subject_name == "Jared Goff"
    assert record.subject_id == "913259"
    assert record.team == "DET"
    assert record.market == "Passing Yards"
    assert record.line == 4000.5
    assert record.period == "regular_season"
    assert record.event_name == "2026 Regular Season"
    assert [selection["side"] for selection in record.selections] == ["More", "Less"]
    assert record.attributes["jersey_number"] == "16"
    assert record.attributes["market_abbreviation"] == "PaYds"


def test_markets_returns_empty_for_invalid_payload():
    adapter = DraftKingsAdapter()

    assert not adapter.markets({"not": "html"})
    assert not adapter.markets("<html>no stream</html>")


def test_players_aggregates_all_stats_without_betting_metadata():
    category = PAGE_DATA["loaderData"]["routes/_homeShared"]
    payload = {
        "categories": [
            {
                "pickCardByPickableId": {
                    key: value["pickCard"]
                    for key, value in category["pickableIdToPickCardMap"].items()
                },
                **category["pickCardLookups"],
            }
        ]
    }

    players = DraftKingsAdapter().players(payload)

    assert len(players) == 1
    assert players[0].full_name == "Jared Goff"
    assert players[0].team == "DET"
    assert players[0].attributes == {
        "provider": "DraftKings",
        "period": "regular_season",
        "projections": {"passing_yards": 4000.5},
    }

    assert DraftKingsAdapter().projection_summaries(payload) == [
        {
            "player": "Jared Goff",
            "team": "DET",
            "period": "regular_season",
            "projections": {"passing_yards": 4000.5},
        }
    ]
