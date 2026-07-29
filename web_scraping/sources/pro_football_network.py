from html import unescape
import re
from typing import Any

from web_scraping.base import FetchedPayload, PlayerRecord, SourceAdapter


PPR_RANKING_PATTERN = re.compile(
    r"(?P<rank>\d+)\)\s*"
    r"<strong>(?P<name>[^<]+)</strong>,\s*"
    r"(?P<position>QB|RB|WR|TE)\s*\|\s*"
    r"(?P<team>[A-Z]{2,3})"
)


class ProFootballNetworkAdapter(SourceAdapter):
    slug = "pro-football-network"
    name = "Pro Football Network"
    base_url = "https://sports.yahoo.com"
    rankings_url = (
        f"{base_url}/articles/"
        "ppr-fantasy-football-rankings-ja-140252724.html"
    )

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        return self.fetch_text(self.rankings_url, timeout)

    def players(self, payload: Any) -> list[PlayerRecord]:
        if not isinstance(payload, str):
            return []
        records = []
        for match in PPR_RANKING_PATTERN.finditer(payload):
            name = unescape(match.group("name"))
            records.append(
                PlayerRecord(
                    external_id=self._name_identifier(name),
                    full_name=name,
                    position=match.group("position"),
                    team=match.group("team"),
                    attributes={
                        "rank": int(match.group("rank")),
                        "scoring_format": "ppr",
                        "points_per_reception": 1,
                        "ranking_type": "overall",
                        "host": "Yahoo Sports",
                        "provider": "Pro Football Network",
                        "source_text": unescape(match.group(0)),
                    },
                )
            )
        return records

    @staticmethod
    def _name_identifier(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
