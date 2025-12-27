"""
Configuration management for the League of Legends Q&A application.
Centralizes all configuration settings for easy maintenance and updates.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class RAGConfig:
    """Configuration for RAG system"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 3
    persist_directory: str = "./chroma_db"
    data_directory: str = "./data"


@dataclass
class LLMConfig:
    """Configuration for LLM"""
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class LangSmithConfig:
    """Configuration for LangSmith monitoring"""
    tracing_enabled: bool = True
    endpoint: str = "https://api.smith.langchain.com"
    project: str = "lolqa"
    api_key: Optional[str] = None


@dataclass
class AppConfig:
    """Application-wide configuration"""
    page_title: str = "League of Legends Q&A Assistant"
    page_icon: str = "⚔️"
    layout: str = "wide"
    port: int = 8501


@dataclass
class DataSourceConfig:
    """Configuration for data sources"""
    use_data_dragon: bool = True  # Riot's public static data API (no key needed)
    use_web_scraper: bool = True  # Web scraping for lore
    use_riot_api: bool = False    # Riot Games API (requires API key)
    use_sample_data: bool = True  # Fallback to sample data
    data_dragon_version: Optional[str] = None  # Auto-detect latest if None
    data_dragon_language: str = "en_US"
    web_scraper_base_url: str = "https://leagueoflegends.fandom.com"
    riot_api_region: str = "na1"


class Config:
    """Main configuration class"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.langsmith_api_key: Optional[str] = os.getenv("LANGSMITH_API_KEY")
        self.riot_api_key: Optional[str] = os.getenv("RIOT_API_KEY")
        
        # RAG Configuration
        self.rag = RAGConfig(
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "200")),
            retrieval_k=int(os.getenv("RAG_RETRIEVAL_K", "3")),
            persist_directory=os.getenv("RAG_PERSIST_DIR", "./chroma_db"),
            data_directory=os.getenv("RAG_DATA_DIR", "./data")
        )
        
        # LLM Configuration
        self.llm = LLMConfig(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None
        )
        
        # LangSmith Configuration
        self.langsmith = LangSmithConfig(
            tracing_enabled=os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true",
            endpoint=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
            project=os.getenv("LANGSMITH_PROJECT", "lolqa"),
            api_key=self.langsmith_api_key
        )
        
        # App Configuration
        self.app = AppConfig(
            page_title=os.getenv("APP_TITLE", "League of Legends Q&A Assistant"),
            page_icon=os.getenv("APP_ICON", "⚔️"),
            layout=os.getenv("APP_LAYOUT", "wide"),
            port=int(os.getenv("APP_PORT", "8501"))
        )
        
        # Data Source Configuration
        self.data_source = DataSourceConfig(
            use_data_dragon=os.getenv("USE_DATA_DRAGON", "true").lower() == "true",
            use_web_scraper=os.getenv("USE_WEB_SCRAPER", "true").lower() == "true",
            use_riot_api=os.getenv("USE_RIOT_API", "false").lower() == "true",
            use_sample_data=os.getenv("USE_SAMPLE_DATA", "true").lower() == "true",
            data_dragon_version=os.getenv("DATA_DRAGON_VERSION"),
            data_dragon_language=os.getenv("DATA_DRAGON_LANGUAGE", "en_US"),
            web_scraper_base_url=os.getenv("WEB_SCRAPER_BASE_URL", "https://leagueoflegends.fandom.com"),
            riot_api_region=os.getenv("RIOT_API_REGION", "na1")
        )
    
    def validate(self) -> tuple:
        """Validate configuration"""
        if not self.openai_api_key:
            return False, "OPENAI_API_KEY is required"
        return True, None
    
    def setup_langsmith(self):
        """Setup LangSmith environment variables"""
        if self.langsmith.tracing_enabled:
            os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
            os.environ.setdefault("LANGCHAIN_ENDPOINT", self.langsmith.endpoint)
            os.environ.setdefault("LANGCHAIN_API_KEY", self.langsmith.api_key or "")
            os.environ.setdefault("LANGCHAIN_PROJECT", self.langsmith.project)


# Global configuration instance
config = Config()

