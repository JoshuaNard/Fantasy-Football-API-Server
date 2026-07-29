from html import unescape
import re
from typing import Any

from web_scraping.base import FetchedPayload, PlayerRecord, SourceAdapter


ESPN_RANKING_PATTERN = re.compile(
    r"(?P<rank>\d+)\.\s*"
    r"<a\s+href=[\"'](?P<href>[^\"']+)[\"'][^>]*>"
    r"(?P<name>[^<]+)</a>(?:\s+DST)?,\s*(?P<team>[A-Z]{2,3})\s*"
    r"\((?P<position>QB|RB|WR|TE|K|DST)(?P<position_rank>\d+)\)",
    re.IGNORECASE,
)
ESPN_PLAYER_ID_PATTERN = re.compile(r"/nfl/player/_/id/(?P<player_id>\d+)/")


class EspnAdapter(SourceAdapter):
    slug = "espn"
    name = "ESPN"
    base_url = "https://www.espn.com"
    rankings_url = (
        f"{base_url}/fantasy/football/story/_/id/48711830/"
        "2026-fantasy-football-rankings-ppr-field-yates"
    )

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        return self.fetch_text(self.rankings_url, timeout)

    def players(self, payload: Any) -> list[PlayerRecord]:
        if not isinstance(payload, str):
            return []
        records = []
        for match in ESPN_RANKING_PATTERN.finditer(payload):
            name = unescape(match.group("name")).strip()
            position = match.group("position").upper()
            id_match = ESPN_PLAYER_ID_PATTERN.search(match.group("href"))
            player_id = (
                id_match.group("player_id")
                if id_match
                else f"dst-{match.group('team').lower()}"
            )
            if position == "DST":
                name = f"{name} D/ST"
            records.append(
                PlayerRecord(
                    external_id=player_id,
                    full_name=name,
                    position=position,
                    team=match.group("team"),
                    attributes={
                        "rank": int(match.group("rank")),
                        "rank_scope": "overall",
                        "position_rank": int(match.group("position_rank")),
                        "scoring_format": "ppr",
                        "points_per_reception": 1,
                        "espn_player_id": (
                            id_match.group("player_id") if id_match else None
                        ),
                        "provider": "ESPN",
                        "analyst": "Field Yates",
                        "source_text": unescape(match.group(0)),
                    },
                )
            )
        return records
