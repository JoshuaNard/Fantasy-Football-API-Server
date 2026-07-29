from dataclasses import dataclass, field
import json
from typing import Any
from urllib.request import Request, urlopen


USER_AGENT = "FantasyFootballAPI/0.1 (+data-collection)"


@dataclass(frozen=True)
class FetchedPayload:
    url: str
    status: int
    content_type: str
    headers: dict[str, str]
    payload: Any


@dataclass(frozen=True)
class PlayerRecord:
    external_id: str
    full_name: str
    first_name: str = ""
    last_name: str = ""
    position: str = ""
    team: str = ""
    active: bool = True
    attributes: dict[str, Any] = field(default_factory=dict)


class SourceAdapter:
    slug: str
    name: str
    base_url: str

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        raise NotImplementedError

    def players(self, _payload: Any) -> list[PlayerRecord]:
        return []

    @staticmethod
    def fetch_json(url: str, timeout: int) -> FetchedPayload:
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return FetchedPayload(
                url=url,
                status=response.status,
                content_type=response.headers.get_content_type(),
                headers={
                    key: value
                    for key, value in response.headers.items()
                    if key.lower() not in {"set-cookie", "authorization"}
                },
                payload=json.loads(body),
            )
