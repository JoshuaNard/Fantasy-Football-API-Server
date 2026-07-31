"""Print combined Vegas-derived player projections."""

from web_scraping.debug import records_as_json
from web_scraping.projections import combine_player_projections
from web_scraping.sources.draftkings import DraftKingsAdapter
from web_scraping.sources.fanduel import FanDuelAdapter
from web_scraping.sources.kalshi import KalshiAdapter


def main() -> None:
    adapters = [DraftKingsAdapter(), FanDuelAdapter(), KalshiAdapter()]
    source_players = []
    for adapter in adapters:
        fetched = adapter.fetch()
        source = (
            "kalshi_market_implied"
            if adapter.slug == "kalshi"
            else adapter.slug
        )
        source_players.append((source, adapter.players(fetched.payload)))
    print(records_as_json(combine_player_projections(source_players)))


if __name__ == "__main__":
    main()
