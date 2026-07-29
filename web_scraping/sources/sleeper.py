from typing import Any

from web_scraping.base import FetchedPayload, PlayerRecord, SourceAdapter


class SleeperAdapter(SourceAdapter):
    slug = "sleeper"
    name = "Sleeper"
    base_url = "https://api.sleeper.app"
    players_url = f"{base_url}/v1/players/nfl"

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        return self.fetch_json(self.players_url, timeout)

    def players(self, payload: Any) -> list[PlayerRecord]:
        records = []
        for external_id, data in payload.items():
            if not isinstance(data, dict):
                continue
            full_name = data.get("full_name") or " ".join(
                part
                for part in (data.get("first_name"), data.get("last_name"))
                if part
            )
            if not full_name:
                continue
            records.append(
                PlayerRecord(
                    external_id=str(external_id),
                    full_name=full_name,
                    first_name=data.get("first_name") or "",
                    last_name=data.get("last_name") or "",
                    position=data.get("position") or "",
                    team=data.get("team") or "",
                    active=bool(data.get("active", True)),
                    attributes=data,
                )
            )
        return records
