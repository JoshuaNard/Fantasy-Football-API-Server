from web_scraping.sources.pro_football_network import ProFootballNetworkAdapter
from web_scraping.sources.sleeper import SleeperAdapter


ADAPTERS = {
    ProFootballNetworkAdapter.slug: ProFootballNetworkAdapter,
    SleeperAdapter.slug: SleeperAdapter,
}
