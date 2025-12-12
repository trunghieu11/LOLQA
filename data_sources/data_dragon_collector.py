"""
Data Dragon Collector - Fetches static League of Legends data.
Data Dragon is Riot's static data API (no API key required).
"""
import requests
from typing import List, Dict, Optional
from langchain_core.documents import Document
from data_sources.base_collector import BaseDataCollector
from utils import logger


class DataDragonCollector(BaseDataCollector):
    """
    Collects data from Riot's Data Dragon API.
    No API key required - public static data.
    """
    
    def __init__(self, version: Optional[str] = None, language: str = "en_US"):
        """
        Initialize Data Dragon collector.
        
        Args:
            version: Game version (e.g., "14.1.1"). If None, fetches latest.
            language: Language code (default: "en_US")
        """
        self.language = language
        self.base_url = "https://ddragon.leagueoflegends.com"
        self.version = version or self._get_latest_version()
        logger.info(f"DataDragonCollector initialized with version {self.version}")
    
    def _get_latest_version(self) -> str:
        """Get the latest game version from Data Dragon"""
        try:
            response = requests.get(f"{self.base_url}/api/versions.json", timeout=10)
            response.raise_for_status()
            versions = response.json()
            return versions[0]  # Latest version is first
        except Exception as e:
            logger.warning(f"Could not fetch latest version, using fallback: {e}")
            return "14.1.1"  # Fallback version
    
    def get_name(self) -> str:
        """Get collector name"""
        return "DataDragon"
    
    def collect(self) -> List[Document]:
        """
        Collect champion data from Data Dragon.
        
        Returns:
            List of Document objects
        """
        documents = []
        
        try:
            # Fetch champion data
            champ_url = f"{self.base_url}/cdn/{self.version}/data/{self.language}/champion.json"
            logger.info(f"Fetching champion data from {champ_url}")
            
            response = requests.get(champ_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            champions = data.get("data", {})
            logger.info(f"Found {len(champions)} champions")
            
            for champ_id, champ_data in champions.items():
                doc = self._champion_to_document(champ_data)
                documents.append(doc)
            
            logger.info(f"Successfully collected {len(documents)} champion documents")
            
        except Exception as e:
            logger.error(f"Error collecting Data Dragon data: {e}", exc_info=True)
            raise
        
        return documents
    
    def _champion_to_document(self, champ_data: Dict) -> Document:
        """
        Convert champion data to Document.
        
        Args:
            champ_data: Champion data from API
            
        Returns:
            Document object
        """
        name = champ_data.get("name", "")
        title = champ_data.get("title", "")
        blurb = champ_data.get("blurb", "")
        tags = champ_data.get("tags", [])
        roles = ", ".join(tags) if tags else "Unknown"
        
        # Get abilities
        spells = champ_data.get("spells", [])
        abilities_text = ""
        for i, spell in enumerate(spells, 1):
            spell_name = spell.get("name", "")
            spell_description = spell.get("description", "")
            # Clean HTML tags from description
            spell_description = re.sub(r'<[^>]+>', '', spell_description)
            abilities_text += f"- {spell_name}: {spell_description}\n"
        
        # Get passive
        passive = champ_data.get("passive", {})
        passive_name = passive.get("name", "")
        passive_description = passive.get("description", "")
        passive_description = re.sub(r'<[^>]+>', '', passive_description)
        
        content = f"""
Champion: {name}
Title: {title}
Role: {roles}

Description: {blurb}

Passive Ability: {passive_name}
{passive_description}

Abilities:
{abilities_text}

Lore: {champ_data.get("lore", "No lore available")}
"""
        
        return Document(
            page_content=content.strip(),
            metadata={
                "champion": name,
                "champion_id": champ_data.get("id", ""),
                "role": roles,
                "type": "champion",
                "source": "data_dragon",
                "version": self.version
            }
        )
    
    def collect_items(self) -> List[Document]:
        """
        Collect item data from Data Dragon.
        
        Returns:
            List of Document objects for items
        """
        documents = []
        
        try:
            items_url = f"{self.base_url}/cdn/{self.version}/data/{self.language}/item.json"
            logger.info(f"Fetching item data from {items_url}")
            
            response = requests.get(items_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("data", {})
            logger.info(f"Found {len(items)} items")
            
            for item_id, item_data in items.items():
                # Skip items without names (consumables, etc.)
                if not item_data.get("name") or item_data.get("name").startswith("@"):
                    continue
                
                name = item_data.get("name", "")
                description = item_data.get("description", "")
                # Clean HTML tags
                import re
                description = re.sub(r'<[^>]+>', '', description)
                
                content = f"""
Item: {name}
Description: {description}
Cost: {item_data.get("gold", {}).get("total", "Unknown")} gold
"""
                
                documents.append(Document(
                    page_content=content.strip(),
                    metadata={
                        "item": name,
                        "item_id": item_id,
                        "type": "item",
                        "source": "data_dragon",
                        "version": self.version
                    }
                ))
            
            logger.info(f"Successfully collected {len(documents)} item documents")
            
        except Exception as e:
            logger.error(f"Error collecting items: {e}", exc_info=True)
        
        return documents

