from web_scraping.sources.espn import EspnAdapter
from web_scraping.sources.pro_football_network import ProFootballNetworkAdapter
from web_scraping.sources.sleeper import SleeperAdapter


ADAPTERS = {
    EspnAdapter.slug: EspnAdapter,
    ProFootballNetworkAdapter.slug: ProFootballNetworkAdapter,
    SleeperAdapter.slug: SleeperAdapter,
}
