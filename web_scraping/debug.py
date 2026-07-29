"""Developer commands for inspecting normalized scraper output."""

from dataclasses import asdict
import json

from web_scraping.sources.pro_football_network import ProFootballNetworkAdapter


DEBUG_PLAYER_LIMIT = 10


def records_as_json(records) -> str:
    return json.dumps(
        [asdict(record) for record in records[:DEBUG_PLAYER_LIMIT]],
        indent=2,
        ensure_ascii=False,
    )


def main() -> None:
    adapter = ProFootballNetworkAdapter()
    fetched = adapter.fetch()
    print(records_as_json(adapter.players(fetched.payload)))


if __name__ == "__main__":
    main()
