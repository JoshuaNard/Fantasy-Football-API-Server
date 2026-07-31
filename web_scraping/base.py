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


@dataclass(frozen=True)
# A lossless market row needs identity, subject, event, line, and selection fields.
# pylint: disable=too-many-instance-attributes
class MarketRecord:
    """One sportsbook projection/prop line, retained without aggregation."""

    external_id: str
    provider: str
    subject_type: str
    subject_id: str
    subject_name: str
    team: str
    market: str
    line: float
    period: str
    event_id: str
    event_name: str
    event_start: str
    selections: list[dict[str, Any]] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


class SourceAdapter:
    slug: str
    name: str
    base_url: str

    def fetch(self, timeout: int = 60) -> FetchedPayload:
        raise NotImplementedError

    def players(self, _payload: Any) -> list[PlayerRecord]:
        return []

    def markets(self, _payload: Any) -> list[MarketRecord]:
        return []

    @staticmethod
    def fetch_json(
        url: str, timeout: int, request_headers: dict[str, str] | None = None
    ) -> FetchedPayload:
        headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
        headers.update(request_headers or {})
        request = Request(
            url,
            headers=headers,
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

    @staticmethod
    def fetch_text(url: str, timeout: int) -> FetchedPayload:
        request = Request(
            url,
            headers={"Accept": "text/html", "User-Agent": USER_AGENT},
        )
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            encoding = response.headers.get_content_charset() or "utf-8"
            return FetchedPayload(
                url=url,
                status=response.status,
                content_type=response.headers.get_content_type(),
                headers={
                    key: value
                    for key, value in response.headers.items()
                    if key.lower() not in {"set-cookie", "authorization"}
                },
                payload=body.decode(encoding),
            )
