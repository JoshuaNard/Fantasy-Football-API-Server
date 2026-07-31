from web_scraping.base import PlayerRecord
from web_scraping.projections import combine_player_projections


def _player(name, team, projections):
    return PlayerRecord(
        external_id=name.lower().replace(" ", "-"),
        full_name=name,
        team=team,
        attributes={"period": "regular_season", "projections": projections},
    )


def test_combines_sources_and_uses_median_of_available_values():
    draftkings = [
        _player(
            "A.J. Brown",
            "NE",
            {"receiving_yards": 1124.5, "receiving_touchdowns": None},
        )
    ]
    fanduel = [
        _player(
            "A.J. Brown",
            "NE",
            {"receiving_yards": 1099.5, "receiving_touchdowns": 7.5},
        )
    ]
    kalshi = [
        _player(
            "A.J. Brown",
            "",
            {"receiving_yards": 1100, "receptions": 80},
        )
    ]

    result = combine_player_projections(
        [
            ("draftkings", draftkings),
            ("fanduel", fanduel),
            ("kalshi_market_implied", kalshi),
        ]
    )

    assert result == [
        {
            "player": "A.J. Brown",
            "team": "NE",
            "period": "regular_season",
            "projections": {
                "receiving_yards": 1100.0,
                "receiving_touchdowns": 7.5,
                "receptions": 80.0,
            },
            "source_projections": {
                "receiving_yards": {
                    "draftkings": 1124.5,
                    "fanduel": 1099.5,
                    "kalshi_market_implied": 1100.0,
                },
                "receiving_touchdowns": {"fanduel": 7.5},
                "receptions": {"kalshi_market_implied": 80.0},
            },
        }
    ]


def test_matches_punctuation_and_name_suffix_variants():
    result = combine_player_projections(
        [
            ("one", [_player("A.J. Brown", "NE", {"receptions": 80})]),
            ("two", [_player("AJ Brown", "", {"receiving_yards": 1100})]),
            ("three", [_player("AJ Brown Sr.", "", {"receiving_touchdowns": 8})]),
        ]
    )

    assert len(result) == 1
    assert result[0]["projections"] == {
        "receptions": 80.0,
        "receiving_yards": 1100.0,
        "receiving_touchdowns": 8.0,
    }
