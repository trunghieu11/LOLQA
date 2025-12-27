"""Data sources for League of Legends information"""

from src.data.sources.base import BaseDataCollector
from src.data.sources.data_dragon import DataDragonCollector
from src.data.sources.web_scraper import WebScraperCollector
from src.data.sources.riot_api import RiotAPICollector
from src.data.sources.sample_data import SampleDataCollector

__all__ = [
    "BaseDataCollector",
    "DataDragonCollector",
    "WebScraperCollector",
    "RiotAPICollector",
    "SampleDataCollector",
]

