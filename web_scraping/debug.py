"""Developer commands for inspecting normalized scraper output."""

import argparse
from dataclasses import asdict, is_dataclass
import json

from web_scraping.sources import ADAPTERS


DEBUG_PLAYER_LIMIT = 10


def records_as_json(records) -> str:
    return json.dumps(
        [
            asdict(record) if is_dataclass(record) else record
            for record in records[:DEBUG_PLAYER_LIMIT]
        ],
        indent=2,
        ensure_ascii=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", choices=sorted(ADAPTERS))
    arguments = parser.parse_args()
    adapter = ADAPTERS[arguments.source]()
    fetched = adapter.fetch()
    if hasattr(adapter, "projection_summaries"):
        records = adapter.projection_summaries(fetched.payload)
    else:
        records = adapter.players(fetched.payload) or adapter.markets(fetched.payload)
    print(records_as_json(records))


if __name__ == "__main__":
    main()
