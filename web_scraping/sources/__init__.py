from web_scraping.sources.draftkings import DraftKingsAdapter
from web_scraping.sources.espn import EspnAdapter
from web_scraping.sources.fanduel import FanDuelAdapter
from web_scraping.sources.kalshi import KalshiAdapter
from web_scraping.sources.pro_football_network import ProFootballNetworkAdapter
from web_scraping.sources.sleeper import SleeperAdapter


ADAPTERS = {
    DraftKingsAdapter.slug: DraftKingsAdapter,
    EspnAdapter.slug: EspnAdapter,
    FanDuelAdapter.slug: FanDuelAdapter,
    KalshiAdapter.slug: KalshiAdapter,
    ProFootballNetworkAdapter.slug: ProFootballNetworkAdapter,
    SleeperAdapter.slug: SleeperAdapter,
}
