"""Tests for ESPN's first-party PPR rankings scraper."""

# Pylint treats common adapter-test setup as duplicated production code.
# pylint: disable=duplicate-code

from web_scraping.base import FetchedPayload
from web_scraping.sources import ADAPTERS
from web_scraping.sources.espn import EspnAdapter


ESPN_PPR_HTML = """
<html>
  <p>
    1. <a href="https://www.espn.com/nfl/player/_/id/4430807/bijan-robinson">
      Bijan Robinson</a>, ATL (RB1)<br>
    2. <a href="https://www.espn.com/nfl/player/_/id/4429795/jahmyr-gibbs">
      Jahmyr Gibbs</a>, DET (RB2)<br>
    3. <a href="https://www.espn.com/nfl/player/_/id/4426515/puka-nacua">
      Puka Nacua</a>, LAR (WR1)<br>
    4. <a href="https://www.espn.com/nfl/player/_/id/3918298/josh-allen">
      Josh Allen</a>, BUF (QB1)<br>
    5. <a href="https://www.espn.com/nfl/player/_/id/4361307/trey-mcbride">
      Trey McBride</a>, ARI (TE1)<br>
    6. <a href="https://www.espn.com/nfl/player/_/id/3953687/brandon-aubrey">
      Brandon Aubrey</a>, DAL (K1)<br>
    7. <a href="/nfl/team/_/name/hou/houston-texans">
      Houston Texans</a> DST, HOU (DST1)
  </p>
</html>
"""


def test_espn_is_registered():
    assert ADAPTERS["espn"] is EspnAdapter


def test_fetch_uses_anonymous_espn_ppr_rankings_page(monkeypatch):
    expected = FetchedPayload(
        url=EspnAdapter.rankings_url,
        status=200,
        content_type="text/html",
        headers={},
        payload=ESPN_PPR_HTML,
    )
    called = {}

    def fake_fetch_text(url, timeout):
        called.update(url=url, timeout=timeout)
        return expected

    monkeypatch.setattr(EspnAdapter, "fetch_text", staticmethod(fake_fetch_text))

    result = EspnAdapter().fetch(timeout=18)

    assert result is expected
    assert called == {"url": EspnAdapter.rankings_url, "timeout": 18}


def test_players_extracts_ppr_rank_team_position_and_espn_id():
    records = EspnAdapter().players(ESPN_PPR_HTML)

    assert len(records) == 7
    assert records[0].external_id == "4430807"
    assert records[0].full_name == "Bijan Robinson"
    assert records[0].position == "RB"
    assert records[0].team == "ATL"
    assert records[0].attributes["rank"] == 1
    assert records[0].attributes["rank_scope"] == "overall"
    assert records[0].attributes["position_rank"] == 1
    assert records[0].attributes["scoring_format"] == "ppr"
    assert records[0].attributes["points_per_reception"] == 1
    assert records[0].attributes["espn_player_id"] == "4430807"
    assert records[2].position == "WR"
    assert records[2].team == "LAR"
    assert records[3].position == "QB"
    assert records[4].position == "TE"
    assert records[5].position == "K"
    assert records[6].external_id == "dst-hou"
    assert records[6].full_name == "Houston Texans D/ST"
    assert records[6].position == "DST"


def test_players_returns_empty_list_for_non_html_payload():
    assert not EspnAdapter().players({"not": "html"})


def test_players_ignores_links_without_overall_and_position_ranks():
    html = (
        '<a href="https://www.espn.com/nfl/player/_/id/3918298/josh-allen">'
        "Josh Allen</a>, BUF"
    )

    assert not EspnAdapter().players(html)
