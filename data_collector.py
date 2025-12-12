"""
Data Collector for League of Legends Information
Collects and prepares data from multiple sources (APIs, web scraping, etc.)
"""
import os
from typing import List, Optional
from langchain_core.documents import Document
from config import config
from utils import logger
from data_sources import (
    DataDragonCollector,
    WebScraperCollector,
    RiotAPICollector,
    SampleDataCollector,
    BaseDataCollector
)


class LoLDataCollector:
    """
    Main data collector that aggregates data from multiple sources.
    Supports Data Dragon API, web scraping, Riot API, and fallback sample data.
    """
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize the data collector with configured data sources.
        
        Args:
            data_dir: Directory to store data files (defaults to config value)
        """
        self.data_dir = data_dir or config.rag.data_directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data source collectors based on configuration
        self.collectors: List[BaseDataCollector] = []
        self._initialize_collectors()
        
        logger.info(f"LoLDataCollector initialized with {len(self.collectors)} data sources")
    
    def _initialize_collectors(self):
        """Initialize data source collectors based on configuration"""
        ds_config = config.data_source
        
        # Data Dragon (public API, no key needed) - Recommended
        if ds_config.use_data_dragon:
            try:
                collector = DataDragonCollector(
                    version=ds_config.data_dragon_version,
                    language=ds_config.data_dragon_language
                )
                self.collectors.append(collector)
                logger.info("Data Dragon collector enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Data Dragon collector: {e}")
        
        # Web Scraper (for lore and additional data)
        if ds_config.use_web_scraper:
            try:
                collector = WebScraperCollector(
                    base_url=ds_config.web_scraper_base_url
                )
                self.collectors.append(collector)
                logger.info("Web scraper collector enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize web scraper: {e}")
        
        # Riot API (requires API key, rate-limited)
        if ds_config.use_riot_api:
            try:
                collector = RiotAPICollector(
                    api_key=config.riot_api_key,
                    region=ds_config.riot_api_region
                )
                is_valid, error_msg = collector.validate()
                if is_valid:
                    self.collectors.append(collector)
                    logger.info("Riot API collector enabled")
                else:
                    logger.warning(f"Riot API collector disabled: {error_msg}")
            except Exception as e:
                logger.warning(f"Failed to initialize Riot API collector: {e}")
        
        # Sample Data (fallback)
        if ds_config.use_sample_data:
            collector = SampleDataCollector()
            self.collectors.append(collector)
            logger.info("Sample data collector enabled (fallback)")
        
        # Ensure at least one collector is available
        if not self.collectors:
            logger.warning("No data collectors available! Adding sample data collector as fallback.")
            self.collectors.append(SampleDataCollector())
    
    def get_documents(self) -> List[Document]:
        """
        Get all documents from all enabled data sources.
        
        Returns:
            List of Document objects ready for embedding
        """
        all_documents = []
        successful_sources = []
        failed_sources = []
        
        logger.info(f"Collecting data from {len(self.collectors)} sources...")
        
        for collector in self.collectors:
            collector_name = collector.get_name()
            try:
                logger.info(f"Collecting from {collector_name}...")
                documents = collector.collect()
                
                if documents:
                    all_documents.extend(documents)
                    successful_sources.append(collector_name)
                    logger.info(f"✓ {collector_name}: Collected {len(documents)} documents")
                else:
                    logger.warning(f"⚠ {collector_name}: No documents collected")
                    failed_sources.append(collector_name)
                    
            except Exception as e:
                logger.error(f"✗ {collector_name}: Failed to collect data - {e}", exc_info=True)
                failed_sources.append(collector_name)
        
        # Summary
        logger.info(f"Data collection complete:")
        logger.info(f"  ✓ Successful: {', '.join(successful_sources) if successful_sources else 'None'}")
        if failed_sources:
            logger.warning(f"  ✗ Failed: {', '.join(failed_sources)}")
        logger.info(f"  Total documents: {len(all_documents)}")
        
        # If no documents collected, ensure we have at least sample data
        if not all_documents:
            logger.warning("No documents collected from any source! Using sample data as fallback.")
            sample_collector = SampleDataCollector()
            all_documents = sample_collector.collect()
        
        return all_documents
    
    def get_champion_documents(self) -> List[Document]:
        """
        Get only champion-related documents.
        
        Returns:
            List of Document objects about champions
        """
        all_docs = self.get_documents()
        return [doc for doc in all_docs if doc.metadata.get("type") == "champion"]
    
    def get_lore_documents(self) -> List[Document]:
        """
        Get only lore-related documents.
        
        Returns:
            List of Document objects about lore
        """
        all_docs = self.get_documents()
        return [doc for doc in all_docs if "lore" in doc.metadata.get("type", "").lower()]
    
    def get_item_documents(self) -> List[Document]:
        """
        Get only item-related documents.
        
        Returns:
            List of Document objects about items
        """
        all_docs = self.get_documents()
        return [doc for doc in all_docs if doc.metadata.get("type") == "item"]
    
    def refresh_data(self) -> List[Document]:
        """
        Force refresh data from all sources.
        Useful for updating the knowledge base.
        
        Returns:
            List of fresh Document objects
        """
        logger.info("Refreshing data from all sources...")
        return self.get_documents()

