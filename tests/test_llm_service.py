"""Tests for LLM Service"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.llm_service.main import app
from services.llm_service.llm_client import LLMClient
from shared.common.config import LLMServiceConfig


class TestLLMServiceAPI:
    """Test LLM Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @patch('services.llm_service.main.LLMClient')
    @patch('services.llm_service.main.RedisClient')
    def test_health_check(self, mock_redis, mock_llm_client, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "llm-service"
    
    @patch('services.llm_service.main.llm_client')
    @patch('services.llm_service.main.redis_client')
    def test_chat_completion(self, mock_redis, mock_llm_client, client):
        """Test chat completion endpoint"""
        # Mock LLM client response
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_response.model = "gpt-4o-mini"
        mock_llm_client.chat = AsyncMock(return_value=mock_response)
        
        response = client.post(
            "/chat",
            json={
                "messages": [
                    {"role": "user", "content": "Hello"}
                ]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert data["content"] == "Test response"
    
    @patch('services.llm_service.main.llm_client')
    @patch('services.llm_service.main.redis_client')
    def test_embeddings_with_cache(self, mock_redis, mock_llm_client, client):
        """Test embeddings endpoint with caching"""
        import json
        
        # Mock Redis cache miss then hit
        mock_redis_client = MagicMock()
        mock_redis_client.get.return_value = None  # Cache miss
        mock_redis_client.set.return_value = True
        
        # Mock LLM client
        mock_embeddings_response = MagicMock()
        mock_embeddings_response.embeddings = [[0.1] * 1536]
        mock_embeddings_response.model = "text-embedding-3-small"
        mock_llm_client.embeddings = AsyncMock(return_value=mock_embeddings_response)
        
        # Replace redis_client in app
        import services.llm_service.main as llm_main
        llm_main.redis_client = mock_redis_client
        
        response = client.post(
            "/embeddings",
            json={
                "texts": ["test text"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "embeddings" in data
        assert len(data["embeddings"]) == 1
    
    @patch('services.llm_service.main.llm_client')
    def test_list_models(self, mock_llm_client, client):
        """Test list models endpoint"""
        mock_llm_client.list_models = AsyncMock(return_value=["gpt-4o", "gpt-4o-mini"])
        
        response = client.get("/models")
        
        assert response.status_code == 200
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
    
    @patch('services.llm_service.main.llm_client')
    def test_metrics_endpoint(self, mock_llm_client, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestLLMClient:
    """Test LLM Client"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return LLMServiceConfig(
            service_name="llm-service",
            backend="openai",
            openai_api_key="test-key",
            default_model="gpt-4o-mini"
        )
    
    @patch('services.llm_service.llm_client.ChatOpenAI')
    @patch('services.llm_service.llm_client.OpenAIEmbeddings')
    def test_init_openai(self, mock_embeddings, mock_chat, config):
        """Test OpenAI client initialization"""
        client = LLMClient(config)
        
        assert client.backend == "openai"
        mock_chat.assert_called_once()
        mock_embeddings.assert_called_once()
    
    @patch('services.llm_service.llm_client.ChatOpenAI')
    def test_chat_completion(self, mock_chat, config):
        """Test chat completion"""
        from langchain_core.messages import HumanMessage
        
        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test response"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_chat.return_value = mock_llm
        
        client = LLMClient(config)
        
        import asyncio
        result = asyncio.run(client.chat([
            {"role": "user", "content": "Hello"}
        ]))
        
        assert result.content == "Test response"
    
    @patch('services.llm_service.llm_client.OpenAIEmbeddings')
    def test_embeddings(self, mock_embeddings, config):
        """Test embeddings generation"""
        mock_emb = MagicMock()
        mock_emb.aembed_documents = AsyncMock(return_value=[[0.1] * 1536])
        mock_embeddings.return_value = mock_emb
        
        client = LLMClient(config)
        
        import asyncio
        result = asyncio.run(client.embeddings(["test text"]))
        
        assert len(result.embeddings) == 1
        assert len(result.embeddings[0]) == 1536

