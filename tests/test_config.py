"""
Unit tests for configuration
"""
import pytest
import os
from src.config.settings import (
    RAGConfig,
    LLMConfig,
    LangSmithConfig,
    AppConfig,
    DataSourceConfig,
    Config,
    config
)


class TestRAGConfig:
    """Tests for RAG configuration"""
    
    def test_rag_config_defaults(self):
        """Test RAG config default values"""
        rag_config = RAGConfig()
        
        assert rag_config.chunk_size == 1000
        assert rag_config.chunk_overlap == 200
        assert rag_config.retrieval_k == 3
        assert rag_config.persist_directory == "./chroma_db"
        assert rag_config.data_directory == "./data"
    
    def test_rag_config_custom_values(self):
        """Test RAG config with custom values"""
        rag_config = RAGConfig(
            chunk_size=500,
            chunk_overlap=100,
            retrieval_k=5
        )
        
        assert rag_config.chunk_size == 500
        assert rag_config.chunk_overlap == 100
        assert rag_config.retrieval_k == 5


class TestLLMConfig:
    """Tests for LLM configuration"""
    
    def test_llm_config_defaults(self):
        """Test LLM config default values"""
        llm_config = LLMConfig()
        
        assert llm_config.model == "gpt-4o-mini"
        assert llm_config.temperature == 0.7
        assert llm_config.max_tokens is None
    
    def test_llm_config_custom_values(self):
        """Test LLM config with custom values"""
        llm_config = LLMConfig(
            model="gpt-4",
            temperature=0.5,
            max_tokens=1000
        )
        
        assert llm_config.model == "gpt-4"
        assert llm_config.temperature == 0.5
        assert llm_config.max_tokens == 1000


class TestLangSmithConfig:
    """Tests for LangSmith configuration"""
    
    def test_langsmith_config_defaults(self):
        """Test LangSmith config default values"""
        ls_config = LangSmithConfig()
        
        assert ls_config.tracing_enabled is True
        assert ls_config.endpoint == "https://api.smith.langchain.com"
        assert ls_config.project == "lolqa"
    
    def test_langsmith_config_with_api_key(self):
        """Test LangSmith config with API key"""
        ls_config = LangSmithConfig(api_key="test-key")
        assert ls_config.api_key == "test-key"


class TestAppConfig:
    """Tests for App configuration"""
    
    def test_app_config_defaults(self):
        """Test App config default values"""
        app_config = AppConfig()
        
        assert app_config.page_title == "League of Legends Q&A Assistant"
        assert app_config.page_icon == "⚔️"
        assert app_config.layout == "wide"
        assert app_config.port == 8501


class TestDataSourceConfig:
    """Tests for Data Source configuration"""
    
    def test_data_source_config_defaults(self):
        """Test Data Source config default values"""
        ds_config = DataSourceConfig()
        
        assert ds_config.use_data_dragon is True
        assert ds_config.use_web_scraper is True
        assert ds_config.use_riot_api is False


class TestConfig:
    """Tests for global Config object"""
    
    def test_config_initialization(self):
        """Test that config is properly initialized"""
        assert config is not None
        assert isinstance(config.rag, RAGConfig)
        assert isinstance(config.llm, LLMConfig)
        assert isinstance(config.langsmith, LangSmithConfig)
        assert isinstance(config.app, AppConfig)
        assert isinstance(config.data_source, DataSourceConfig)
    
    def test_config_openai_api_key(self, monkeypatch):
        """Test OpenAI API key loading"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
        test_config = Config()
        assert test_config.openai_api_key == "test-openai-key"
    
    def test_config_langsmith_api_key(self, monkeypatch):
        """Test LangSmith API key loading"""
        monkeypatch.setenv("LANGSMITH_API_KEY", "test-langsmith-key")
        test_config = Config()
        assert test_config.langsmith_api_key == "test-langsmith-key"
    
    def test_config_riot_api_key(self, monkeypatch):
        """Test Riot API key loading"""
        monkeypatch.setenv("RIOT_API_KEY", "test-riot-key")
        test_config = Config()
        assert test_config.riot_api_key == "test-riot-key"

