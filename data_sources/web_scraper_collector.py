"""
Web Scraper Collector - Scrapes League of Legends wiki for lore and additional data.
"""
import requests
from typing import List, Optional
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from data_sources.base_collector import BaseDataCollector
from utils import logger


class WebScraperCollector(BaseDataCollector):
    """
    Collects data from League of Legends wiki and other web sources.
    """
    
    def __init__(self, base_url: str = "https://leagueoflegends.fandom.com"):
        """
        Initialize web scraper collector.
        
        Args:
            base_url: Base URL for the wiki
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        logger.info(f"WebScraperCollector initialized for {base_url}")
    
    def get_name(self) -> str:
        """Get collector name"""
        return "WebScraper"
    
    def collect(self) -> List[Document]:
        """
        Collect lore and additional data from web sources.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        # Collect game mechanics and lore
        try:
            # Game mechanics page
            mechanics_doc = self._scrape_page(
                f"{self.base_url}/wiki/Game_Mechanics",
                "game_mechanics"
            )
            if mechanics_doc:
                documents.append(mechanics_doc)
            
            # Lore page
            lore_doc = self._scrape_page(
                f"{self.base_url}/wiki/Lore",
                "lore"
            )
            if lore_doc:
                documents.append(lore_doc)
            
            logger.info(f"Successfully collected {len(documents)} web documents")
            
        except Exception as e:
            logger.error(f"Error collecting web data: {e}", exc_info=True)
        
        return documents
    
    def _scrape_page(self, url: str, doc_type: str) -> Optional[Document]:
        """
        Scrape a single page.
        
        Args:
            url: URL to scrape
            doc_type: Type of document
            
        Returns:
            Document object or None if failed
        """
        try:
            logger.info(f"Scraping {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get main content
            main_content = soup.find('div', {'class': 'mw-parser-output'}) or soup.find('main')
            if not main_content:
                main_content = soup.find('body')
            
            if main_content:
                text = main_content.get_text(separator='\n', strip=True)
                # Clean up excessive whitespace
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                content = '\n'.join(lines[:200])  # Limit to first 200 lines
                
                return Document(
                    page_content=content,
                    metadata={
                        "type": doc_type,
                        "source": "web_scraper",
                        "url": url
                    }
                )
            
        except Exception as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        
        return None
    
    def scrape_champion_lore(self, champion_name: str) -> Optional[Document]:
        """
        Scrape detailed lore for a specific champion.
        
        Args:
            champion_name: Name of the champion
            
        Returns:
            Document with champion lore or None
        """
        url = f"{self.base_url}/wiki/{champion_name.replace(' ', '_')}/Lore"
        return self._scrape_page(url, f"champion_lore_{champion_name.lower()}")

