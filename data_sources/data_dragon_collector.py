"""
Data Dragon Collector - Fetches static League of Legends data.
Data Dragon is Riot's static data API (no API key required).
"""
import requests
import re
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
        Fetches both summary data and detailed individual champion files (which include skins).
        
        Returns:
            List of Document objects
        """
        documents = []
        
        try:
            # Fetch champion summary data
            champ_url = f"{self.base_url}/cdn/{self.version}/data/{self.language}/champion.json"
            logger.info(f"Fetching champion data from {champ_url}")
            
            response = requests.get(champ_url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            champions = data.get("data", {})
            logger.info(f"Found {len(champions)} champions")
            
            # Fetch detailed data for each champion (includes skins)
            for champ_id, champ_data in champions.items():
                try:
                    # Fetch individual champion file for detailed info including skins
                    detailed_url = f"{self.base_url}/cdn/{self.version}/data/{self.language}/champion/{champ_id}.json"
                    detailed_response = requests.get(detailed_url, timeout=10)
                    if detailed_response.status_code == 200:
                        detailed_data = detailed_response.json()
                        champ_detailed = detailed_data.get("data", {}).get(champ_id, champ_data)
                        doc = self._champion_to_document(champ_detailed)
                    else:
                        # Fallback to summary data if detailed fetch fails
                        doc = self._champion_to_document(champ_data)
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"Could not fetch detailed data for {champ_id}, using summary: {e}")
                    # Fallback to summary data
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
        Automatically includes ALL available fields from the API.
        
        Args:
            champ_data: Champion data from API
            
        Returns:
            Document object
        """
        content_parts = []
        
        # Basic information
        name = champ_data.get("name", "")
        content_parts.append(f"Champion: {name}")
        
        if champ_data.get("title"):
            content_parts.append(f"Title: {champ_data.get('title')}")
        
        if champ_data.get("tags"):
            roles = ", ".join(champ_data.get("tags", []))
            content_parts.append(f"Roles: {roles}")
        
        if champ_data.get("blurb"):
            content_parts.append(f"\nDescription: {champ_data.get('blurb')}")
        
        # Stats (if available)
        if champ_data.get("stats"):
            stats = champ_data.get("stats", {})
            stats_text = "\nBase Stats:"
            for stat_name, stat_value in stats.items():
                stats_text += f"\n- {stat_name}: {stat_value}"
            content_parts.append(stats_text)
        
        # Passive ability
        if champ_data.get("passive"):
            passive = champ_data.get("passive", {})
            passive_name = passive.get("name", "")
            passive_description = passive.get("description", "")
            passive_description = re.sub(r'<[^>]+>', '', passive_description)
            if passive_name or passive_description:
                content_parts.append(f"\nPassive Ability: {passive_name}")
                if passive_description:
                    content_parts.append(passive_description)
        
        # Abilities (Q, W, E, R)
        if champ_data.get("spells"):
            spells = champ_data.get("spells", [])
            content_parts.append("\nAbilities:")
            for spell in spells:
                spell_name = spell.get("name", "")
                spell_description = spell.get("description", "")
                spell_description = re.sub(r'<[^>]+>', '', spell_description)
                if spell_name:
                    content_parts.append(f"- {spell_name}: {spell_description}")
        
        # Skins (automatically included if available)
        if champ_data.get("skins"):
            skins = champ_data.get("skins", [])
            content_parts.append(f"\nSkins ({len(skins)} total):")
            for skin in skins:
                skin_name = skin.get("name", "")
                skin_num = skin.get("num", 0)
                if skin_num == 0:
                    content_parts.append(f"- {skin_name} (Default)")
                else:
                    content_parts.append(f"- {skin_name}")
        
        # Lore
        if champ_data.get("lore"):
            lore = champ_data.get("lore", "")
            lore = re.sub(r'<[^>]+>', '', lore)
            content_parts.append(f"\nLore: {lore}")
        
        # Include any other fields that might exist in the API
        # This ensures we capture all data without manual updates
        excluded_fields = {"id", "key", "name", "title", "blurb", "tags", "stats", 
                          "passive", "spells", "skins", "lore", "allytips", "enemytips"}
        
        for field_name, field_value in champ_data.items():
            if field_name not in excluded_fields and field_value:
                # Format the field in a readable way
                formatted_value = self._format_field_value(field_value)
                if formatted_value:
                    content_parts.append(f"\n{field_name.replace('_', ' ').title()}: {formatted_value}")
        
        # Ally tips and enemy tips (if available)
        if champ_data.get("allytips"):
            tips = champ_data.get("allytips", [])
            if tips:
                content_parts.append(f"\nAlly Tips:")
                for tip in tips:
                    content_parts.append(f"- {tip}")
        
        if champ_data.get("enemytips"):
            tips = champ_data.get("enemytips", [])
            if tips:
                content_parts.append(f"\nEnemy Tips:")
                for tip in tips:
                    content_parts.append(f"- {tip}")
        
        content = "\n".join(content_parts)
        
        return Document(
            page_content=content.strip(),
            metadata={
                "champion": name,
                "champion_id": champ_data.get("id", ""),
                "champion_key": champ_data.get("key", ""),
                "role": ", ".join(champ_data.get("tags", [])) if champ_data.get("tags") else "Unknown",
                "type": "champion",
                "source": "data_dragon",
                "version": self.version
            }
        )
    
    def _format_field_value(self, value) -> str:
        """
        Format a field value for inclusion in the document.
        Handles various data types automatically.
        
        Args:
            value: Field value (can be dict, list, str, number, etc.)
            
        Returns:
            Formatted string representation
        """
        if isinstance(value, dict):
            # Format dict as key-value pairs
            parts = []
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    v = str(v)
                parts.append(f"{k}: {v}")
            return ", ".join(parts)
        elif isinstance(value, list):
            # Format list items
            if not value:
                return ""
            # If list contains dicts, format them
            if isinstance(value[0], dict):
                return ", ".join([str(item) for item in value])
            return ", ".join([str(item) for item in value])
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, str):
            # Clean HTML tags
            return re.sub(r'<[^>]+>', '', value)
        else:
            return str(value) if value else ""
    
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

