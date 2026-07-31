"""Kalshi NFL season-stat market scraper."""

from collections import defaultdict
from typing import Any

from web_scraping.base import FetchedPayload, PlayerRecord, SourceAdapter


SERIES_TO_STAT = {
    "KXNFLSEASONPASSYDS": "passing_yards",
    "KXNFLSEASONRSHYDS": "rushing_yards",
    "KXNFLSEASONRECYDS": "receiving_yards",
    "KXNFLSEASONREC": "receptions",
    "KXNFLSEASONRSHTD": "rushing_touchdowns",
    "KXNFLSEASONRECTD": "receiving_touchdowns",
}


def _market_probability(market: dict[str, Any]) -> float | None:
    bid = float(market.get("yes_bid_dollars") or 0)
    ask = float(market.get("yes_ask_dollars") or 0)
    if bid and ask:
        return (bid + ask) / 2
    last_price = float(market.get("last_price_dollars") or 0)
    return last_price or None


def _implied_median(points: list[tuple[float, float]]) -> float | None:
    """Estimate the 50% threshold from binary market probabilities."""
    ordered = sorted(points)
    for line, probability in ordered:
        if probability == 0.5:
            return line
    for (lower_line, lower_probability), (
        upper_line,
        upper_probability,
    ) in zip(ordered, ordered[1:]):
        if lower_probability >= 0.5 >= upper_probability:
            probability_range = lower_probability - upper_probability
            if not probability_range:
                return (lower_line + upper_line) / 2
            position = (lower_probability - 0.5) / probability_range
            return lower_line + position * (upper_line - lower_line)
    return min(ordered, key=lambda point: abs(point[1] - 0.5))[0] if ordered else None


class KalshiAdapter(SourceAdapter):
    slug = "kalshi"
    name = "Kalshi"
    base_url = "https://api.elections.kalshi.com/trade-api/v2"

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        series_payloads = {}
        for series in SERIES_TO_STAT:
            url = (
                f"{self.base_url}/events?limit=200&status=open"
                f"&with_nested_markets=true&series_ticker={series}"
            )
            series_payloads[series] = self.fetch_json(url, timeout).payload
        return FetchedPayload(
            url=f"{self.base_url}/events",
            status=200,
            content_type="application/json",
            headers={},
            payload={"series": series_payloads},
        )

    def players(self, payload: Any) -> list[PlayerRecord]:
        if not isinstance(payload, dict):
            return []
        points_by_player = defaultdict(lambda: defaultdict(list))
        for series, response in payload.get("series", {}).items():
            stat = SERIES_TO_STAT.get(series)
            if not stat:
                continue
            for event in response.get("events", []):
                for market in event.get("markets", []):
                    player = market.get("yes_sub_title", "").strip()
                    line = market.get("floor_strike")
                    probability = _market_probability(market)
                    if player and line is not None and probability is not None:
                        points_by_player[player][stat].append(
                            (float(line), probability)
                        )

        records = []
        for player, stat_points in points_by_player.items():
            projections = {
                stat: estimate
                for stat, points in stat_points.items()
                if (estimate := _implied_median(points)) is not None
            }
            records.append(
                PlayerRecord(
                    external_id=player.casefold().replace(" ", "-"),
                    full_name=player,
                    attributes={
                        "provider": self.name,
                        "period": "regular_season",
                        "estimate_type": "market_implied_median",
                        "projections": projections,
                    },
                )
            )
        return sorted(records, key=lambda record: record.full_name)

    def projection_summaries(self, payload: Any) -> list[dict[str, Any]]:
        return [
            {
                "player": player.full_name,
                "period": player.attributes["period"],
                "estimate_type": player.attributes["estimate_type"],
                "projections": player.attributes["projections"],
            }
            for player in self.players(payload)
        ]
