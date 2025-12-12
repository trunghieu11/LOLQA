"""
Riot Games API Collector - Fetches live data from Riot Games API.
Requires API key from https://developer.riotgames.com/
"""
import os
import requests
from typing import List, Dict, Optional
from langchain_core.documents import Document
from data_sources.base_collector import BaseDataCollector
from utils import logger


class RiotAPICollector(BaseDataCollector):
    """
    Collects data from Riot Games API.
    Requires API key and supports rate limiting.
    """
    
    def __init__(self, api_key: Optional[str] = None, region: str = "na1"):
        """
        Initialize Riot API collector.
        
        Args:
            api_key: Riot Games API key (from .env or parameter)
            region: API region (na1, euw1, kr, etc.)
        """
        self.api_key = api_key or os.getenv("RIOT_API_KEY")
        self.region = region
        self.base_url = f"https://{region}.api.riotgames.com"
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-Riot-Token": self.api_key})
        logger.info(f"RiotAPICollector initialized for region {region}")
    
    def get_name(self) -> str:
        """Get collector name"""
        return "RiotAPI"
    
    def validate(self) -> tuple[bool, str]:
        """Validate API key"""
        if not self.api_key:
            return False, "RIOT_API_KEY not found. Riot API collector will be skipped."
        return True, None
    
    def collect(self) -> List[Document]:
        """
        Collect data from Riot API.
        Note: Riot API is rate-limited and requires API key.
        This is a placeholder for future implementation.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        if not self.api_key:
            logger.warning("Riot API key not available, skipping Riot API collection")
            return documents
        
        # Note: Riot API requires specific endpoints for different data types
        # This is a template - implement specific endpoints as needed
        
        try:
            # Example: Get champion rotations (free champions)
            # This endpoint doesn't require much rate limit
            rotation_url = f"{self.base_url}/lol/platform/v3/champion-rotations"
            response = self.session.get(rotation_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                free_champions = data.get("freeChampionIds", [])
                
                if free_champions:
                    content = f"""
Current Free Champions Rotation:
{', '.join(map(str, free_champions))}

These champions are free to play this week.
"""
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "type": "champion_rotation",
                            "source": "riot_api",
                            "region": self.region
                        }
                    ))
                    logger.info("Collected champion rotation data")
            
        except Exception as e:
            logger.warning(f"Error collecting from Riot API: {e}")
            # Don't raise - allow other collectors to continue
        
        return documents
    
    def get_match_data(self, match_id: str) -> Optional[Document]:
        """
        Get match data for a specific match.
        Requires API key and has rate limits.
        
        Args:
            match_id: Match ID
            
        Returns:
            Document with match data or None
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/lol/match/v5/matches/{match_id}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                match_data = response.json()
                # Process match data into document
                # This is a placeholder - implement full match processing
                return Document(
                    page_content=f"Match data for {match_id}",
                    metadata={"type": "match", "match_id": match_id, "source": "riot_api"}
                )
        
        except Exception as e:
            logger.warning(f"Error fetching match {match_id}: {e}")
        
        return None

