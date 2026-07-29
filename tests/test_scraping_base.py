import json
from urllib.request import Request

import pytest

import web_scraping.base
from web_scraping.base import SourceAdapter, USER_AGENT


class FakeHeaders:
    def get_content_type(self):
        return "application/json"

    def items(self):
        return [
            ("Content-Type", "application/json"),
            ("ETag", "test-etag"),
            ("Set-Cookie", "secret-cookie"),
            ("Authorization", "secret-token"),
        ]


class FakeResponse:
    status = 200
    headers = FakeHeaders()

    def __init__(self, payload):
        self.body = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.body


def test_fetch_json_returns_payload_and_safe_response_metadata(monkeypatch):
    requested = {}

    def fake_urlopen(request, timeout):
        requested["request"] = request
        requested["timeout"] = timeout
        return FakeResponse({"player": {"full_name": "Test Player"}})

    monkeypatch.setattr(web_scraping.base, "urlopen", fake_urlopen)

    result = SourceAdapter.fetch_json("https://example.test/players", timeout=12)

    assert result.url == "https://example.test/players"
    assert result.status == 200
    assert result.content_type == "application/json"
    assert result.payload == {"player": {"full_name": "Test Player"}}
    assert result.headers == {
        "Content-Type": "application/json",
        "ETag": "test-etag",
    }
    assert requested["timeout"] == 12
    assert isinstance(requested["request"], Request)
    assert requested["request"].get_header("Accept") == "application/json"
    assert requested["request"].get_header("User-agent") == USER_AGENT


def test_fetch_json_rejects_invalid_json(monkeypatch):
    response = FakeResponse({})
    response.body = b"not-json"
    monkeypatch.setattr(
        web_scraping.base, "urlopen", lambda request, timeout: response
    )

    with pytest.raises(json.JSONDecodeError):
        SourceAdapter.fetch_json("https://example.test/players", timeout=5)
