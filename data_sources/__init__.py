"""
Data Sources Package
Modular data collection system for League of Legends data.
"""
from data_sources.base_collector import BaseDataCollector
from data_sources.data_dragon_collector import DataDragonCollector
from data_sources.web_scraper_collector import WebScraperCollector
from data_sources.riot_api_collector import RiotAPICollector
from data_sources.sample_data_collector import SampleDataCollector

__all__ = [
    "BaseDataCollector",
    "DataDragonCollector",
    "WebScraperCollector",
    "RiotAPICollector",
    "SampleDataCollector"
]

