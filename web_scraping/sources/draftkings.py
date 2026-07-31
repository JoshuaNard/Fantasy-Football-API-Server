"""DraftKings Pick6 NFL projection scraper."""

import json
import re
from typing import Any

from web_scraping.base import FetchedPayload, MarketRecord, PlayerRecord, SourceAdapter


STREAM_PATTERN = re.compile(
    r"streamController\.enqueue\((?P<payload>\".*?\")\);</script>", re.DOTALL
)


def _unflatten(values: list[Any]) -> Any:
    """Decode the flattened data format emitted by React Router."""
    cache: dict[int, Any] = {}

    def hydrate(index: int) -> Any:
        if index < 0:
            return None
        if index in cache:
            return cache[index]
        value = values[index]
        if isinstance(value, dict):
            result: dict[Any, Any] = {}
            cache[index] = result
            for key_index, item_index in value.items():
                result[hydrate(int(key_index.removeprefix("_")))] = hydrate(item_index)
            return result
        if isinstance(value, list):
            result_list: list[Any] = []
            cache[index] = result_list
            result_list.extend(hydrate(item_index) for item_index in value)
            return result_list
        cache[index] = value
        return value

    return hydrate(0)


def _page_data(html: str) -> dict[str, Any]:
    match = STREAM_PATTERN.search(html)
    if not match:
        return {}
    encoded_stream = json.loads(match.group("payload"))
    flattened = json.loads(encoded_stream)
    decoded = _unflatten(flattened)
    return decoded.get("loaderData", {}).get("routes/_homeShared", {})


class DraftKingsAdapter(SourceAdapter):
    slug = "draftkings"
    name = "DraftKings"
    base_url = "https://pick6.draftkings.com"
    projections_url = f"{base_url}/?sport=NFL%20SZN"
    api_url = "https://api.draftkings.com"

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        page = self.fetch_text(self.projections_url, timeout)
        data = _page_data(page.payload)
        pick_group_id = data.get("pickGroupId")
        category_ids = (
            data.get("pickCardData", {})
            .get("pickCardsByPickGroup", {})
            .get("orderedPickCategoryIds", [])
        )
        categories = []
        for category_id in category_ids:
            url = (
                f"{self.api_url}/pick6/v1/pickgroups/{pick_group_id}"
                f"/category/{category_id}/pickcards"
            )
            categories.append(self.fetch_json(url, timeout).payload)
        return FetchedPayload(
            url=self.projections_url,
            status=page.status,
            content_type="application/json",
            headers=page.headers,
            payload={
                "pick_group_id": pick_group_id,
                "categories": categories,
                "source_page": page.payload,
            },
        )

    @staticmethod
    def _category_data(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, dict):
            return payload.get("categories", [])
        if isinstance(payload, str):
            page = _page_data(payload)
            initial = page.get("pickCardData", {}).get("pickCardsByPickGroup", {})
            if not initial and page.get("pickableIdToPickCardMap"):
                lookups = page.get("pickCardLookups", {})
                initial = {
                    "pickCardByPickableId": {
                        key: value.get("pickCard", {})
                        for key, value in page["pickableIdToPickCardMap"].items()
                    },
                    **lookups,
                }
            return [initial] if initial else []
        return []

    # The local names mirror distinct fields in DraftKings' nested market schema.
    # pylint: disable=too-many-locals
    def markets(self, payload: Any) -> list[MarketRecord]:
        records = []
        for category in self._category_data(payload):
            cards = category.get("pickCardByPickableId", {})
            entities = category.get("entityInfoByDkId", {})
            competitions = category.get("competitionById", {})
            teams = category.get("displayTeamById", {})
            market_names = category.get("pickSixMarketById", {})
            for card in cards.values():
                entity = (card.get("entities") or [{}])[0]
                subject_id = str(entity.get("dkId", ""))
                subject = entities.get(subject_id, {})
                competition_id = str((entity.get("compIds") or [""])[0])
                competition = competitions.get(competition_id, {})
                team_id = str(
                    competition.get("entityCompByDkId", {})
                    .get(subject_id, {})
                    .get("teamId", "")
                )
                for market in card.get("activePickableMarkets", []):
                    market_id = str(market.get("pickSixMarketId", ""))
                    market_info = market_names.get(market_id, {})
                    propositions = market_info.get("propositionNameById", {})
                    selections = [
                        {
                            "external_id": str(
                                selection.get("pickableMarketSelectionId", "")
                            ),
                            "side": propositions.get(
                                str(selection.get("statLinePropositionId", "")), ""
                            ),
                            "multiplier": selection.get("standingsMultiplier"),
                        }
                        for selection in market.get("activeSelections", [])
                    ]
                    records.append(
                        MarketRecord(
                            external_id=str(market.get("pickableMarketId", "")),
                            provider=self.name,
                            subject_type="player",
                            subject_id=subject_id,
                            subject_name=subject.get(
                                "fullName", subject.get("name", "")
                            ),
                            team=teams.get(team_id, {}).get("name", ""),
                            market=market_info.get("name", ""),
                            line=float(market["targetValue"]),
                            period="regular_season",
                            event_id=competition_id,
                            event_name=competition.get("name", ""),
                            event_start=competition.get("startTime", ""),
                            selections=selections,
                            attributes={
                                "jersey_number": subject.get("jerseyNum", ""),
                                "market_abbreviation": market_info.get(
                                    "abbreviation", ""
                                ),
                            },
                        )
                    )
        return records

    def players(self, payload: Any) -> list[PlayerRecord]:
        """Aggregate every available projection line into one row per player."""
        players: dict[str, PlayerRecord] = {}
        for market in self.markets(payload):
            stat_name = re.sub(r"[^a-z0-9]+", "_", market.market.lower()).strip("_")
            existing = players.get(market.subject_id)
            projections = (
                dict(existing.attributes["projections"]) if existing else {}
            )
            projections[stat_name] = market.line
            players[market.subject_id] = PlayerRecord(
                external_id=market.subject_id,
                full_name=market.subject_name,
                team=market.team,
                attributes={
                    "provider": self.name,
                    "period": market.period,
                    "projections": projections,
                },
            )
        return sorted(players.values(), key=lambda player: player.full_name)

    def projection_summaries(self, payload: Any) -> list[dict[str, Any]]:
        """Return prediction-focused output without sportsbook plumbing."""
        return [
            {
                "player": player.full_name,
                "team": player.team,
                "period": player.attributes["period"],
                "projections": player.attributes["projections"],
            }
            for player in self.players(payload)
        ]
