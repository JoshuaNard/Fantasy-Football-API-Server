"""FanDuel NFL regular-season projection scraper."""

from collections import defaultdict
import re
from typing import Any

from web_scraping.base import FetchedPayload, PlayerRecord, SourceAdapter


MARKET_PATTERN = re.compile(
    r"^(?P<player>.+?) Regular Season (?P<stat>.+?) \d{4}-\d{2}$"
)
LINE_PATTERN = re.compile(r"\b(?:Over|Under)\s+(?P<line>\d+(?:\.\d+)?)$")
STAT_NAMES = {
    "Passing Yards": "passing_yards",
    "Passing TDs": "passing_touchdowns",
    "Rushing Yards": "rushing_yards",
    "Rushing TDs": "rushing_touchdowns",
    "Receiving Yards": "receiving_yards",
    "Receiving TDs": "receiving_touchdowns",
    "Receptions": "receptions",
}


class FanDuelAdapter(SourceAdapter):
    slug = "fanduel"
    name = "FanDuel"
    base_url = "https://sbapi.nj.sportsbook.fanduel.com"
    projections_url = (
        f"{base_url}/api/content-managed-page?page=CUSTOM&customPageId=nfl"
        "&pbHorizontal=false&_ak=FhMFpcPWXMeyZxOx"
        "&timezone=America%2FNew_York"
    )

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        return self.fetch_json(self.projections_url, timeout)

    def players(self, payload: Any) -> list[PlayerRecord]:
        if not isinstance(payload, dict):
            return []
        projections = defaultdict(dict)
        for market in payload.get("attachments", {}).get("markets", {}).values():
            match = MARKET_PATTERN.match(market.get("marketName", ""))
            if not match or match.group("stat") not in STAT_NAMES:
                continue
            active_runners = [
                runner
                for runner in market.get("runners", [])
                if runner.get("runnerStatus") == "ACTIVE"
            ]
            line_match = next(
                (
                    LINE_PATTERN.search(runner.get("runnerName", ""))
                    for runner in active_runners
                    if LINE_PATTERN.search(runner.get("runnerName", ""))
                ),
                None,
            )
            if line_match:
                projections[match.group("player")][
                    STAT_NAMES[match.group("stat")]
                ] = float(line_match.group("line"))

        return [
            PlayerRecord(
                external_id=name.casefold().replace(" ", "-"),
                full_name=name,
                attributes={
                    "provider": self.name,
                    "period": "regular_season",
                    "projections": stats,
                },
            )
            for name, stats in sorted(projections.items())
        ]

    def projection_summaries(self, payload: Any) -> list[dict[str, Any]]:
        return [
            {
                "player": player.full_name,
                "period": player.attributes["period"],
                "projections": player.attributes["projections"],
            }
            for player in self.players(payload)
        ]
