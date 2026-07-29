"""Tests for the Yahoo-hosted Pro Football Network rankings scraper."""

# Pylint treats common adapter-test setup as duplicated production code.
# pylint: disable=duplicate-code

from web_scraping.base import FetchedPayload
from web_scraping.sources import ADAPTERS
from web_scraping.sources.pro_football_network import ProFootballNetworkAdapter


YAHOO_PPR_HTML = """
<html>
  <h2>Updated PPR Fantasy Football Rankings</h2>
  <p>
    1) <strong>Bijan Robinson</strong>, RB | ATL<br>
    2) <strong>Jahmyr Gibbs</strong>, RB | DET<br>
    3) <strong>Ja&#x2019;Marr Chase</strong>, WR | CIN
  </p>
  <p>Analysis and unrelated text should be ignored.</p>
  <p>4) <strong>Josh Allen</strong>, QB | BUF</p>
  <p>5) <strong>Invalid Player</strong>, LS | FA</p>
</html>
"""


def test_pro_football_network_is_registered():
    assert (
        ADAPTERS["pro-football-network"] is ProFootballNetworkAdapter
    )


def test_fetch_uses_anonymous_full_ppr_article(monkeypatch):
    expected = FetchedPayload(
        url=ProFootballNetworkAdapter.rankings_url,
        status=200,
        content_type="text/html",
        headers={},
        payload=YAHOO_PPR_HTML,
    )
    called = {}

    def fake_fetch_text(url, timeout):
        called.update(url=url, timeout=timeout)
        return expected

    monkeypatch.setattr(
        ProFootballNetworkAdapter, "fetch_text", staticmethod(fake_fetch_text)
    )

    result = ProFootballNetworkAdapter().fetch(timeout=18)

    assert result is expected
    assert called == {
        "url": ProFootballNetworkAdapter.rankings_url,
        "timeout": 18,
    }


def test_players_extracts_only_full_ppr_rankings_with_team_and_position():
    records = ProFootballNetworkAdapter().players(YAHOO_PPR_HTML)

    assert len(records) == 4
    assert records[0].external_id == "bijan-robinson"
    assert records[0].full_name == "Bijan Robinson"
    assert records[0].position == "RB"
    assert records[0].team == "ATL"
    assert records[0].attributes == {
        "rank": 1,
        "scoring_format": "ppr",
        "points_per_reception": 1,
        "ranking_type": "overall",
        "host": "Yahoo Sports",
        "provider": "Pro Football Network",
        "source_text": (
            "1) <strong>Bijan Robinson</strong>, RB | ATL"
        ),
    }
    assert records[2].full_name == "Ja’Marr Chase"
    assert records[2].position == "WR"
    assert records[2].team == "CIN"
    assert records[3].full_name == "Josh Allen"
    assert records[3].position == "QB"
    assert records[3].team == "BUF"


def test_players_returns_empty_list_for_non_html_payload():
    assert not ProFootballNetworkAdapter().players({"not": "html"})


def test_players_returns_empty_list_when_ppr_rankings_are_missing():
    assert not ProFootballNetworkAdapter().players(
        "<p>1. Josh Allen - standard ranking without team metadata</p>"
    )
