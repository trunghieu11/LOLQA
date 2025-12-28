"""Tests for RAG Service"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import using helper to handle hyphenated directory names
from tests.import_helpers import import_service_module

try:
    rag_module = import_service_module("rag-service", "main")
    app = rag_module.app
    
    from shared.common.config import RAGServiceConfig
except (ImportError, AttributeError) as e:
    pytest.skip(f"Could not import RAG service: {e}", allow_module_level=True)


class TestRAGServiceAPI:
    """Test RAG Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @patch('services.rag_service.main.RAGServiceSystem')
    def test_health_check(self, mock_rag_system, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "rag-service"
    
    @patch('services.rag_service.main.rag_system')
    def test_query(self, mock_rag_system, client):
        """Test RAG query endpoint"""
        # Mock RAG system
        mock_rag_system.query = AsyncMock(return_value="Test answer")
        mock_rag_system.get_relevant_documents = AsyncMock(return_value=[])
        
        response = client.post(
            "/query",
            json={
                "question": "What are Ahri's abilities?",
                "k": 3
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert data["answer"] == "Test answer"
    
    @patch('services.rag_service.main.rag_system')
    def test_retrieve(self, mock_rag_system, client):
        """Test retrieve endpoint"""
        from langchain_core.documents import Document
        
        mock_docs = [
            Document(page_content="Test content", metadata={"type": "champion"})
        ]
        mock_rag_system.get_relevant_documents = AsyncMock(return_value=mock_docs)
        
        response = client.post("/retrieve?question=test&k=3")
        
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert len(data["documents"]) == 1
    
    @patch('services.rag_service.main.rag_system')
    def test_stats(self, mock_rag_system, client):
        """Test stats endpoint"""
        mock_rag_system.get_stats = AsyncMock(return_value={
            "total_documents": 100,
            "vector_db_path": "/app/chroma_db"
        })
        
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data


class TestRAGServiceSystem:
    """Test RAG Service System"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return RAGServiceConfig(
            service_name="rag-service",
            llm_service_url="http://llm-service:8000",
            vector_db_path="./test_chroma_db"
        )
    
    @patch('services.rag_service.rag_system.OpenAIEmbeddings')
    @patch('services.rag_service.rag_system.Chroma')
    def test_initialize(self, mock_chroma, mock_embeddings, config):
        """Test RAG system initialization"""
        from services.rag_service.rag_system import RAGServiceSystem
        
        mock_vectorstore = MagicMock()
        mock_chroma.return_value = mock_vectorstore
        
        system = RAGServiceSystem(config)
        
        import asyncio
        asyncio.run(system.initialize())
        
        assert system.vectorstore is not None
    
    @patch('services.rag_service.rag_system.LLMServiceClient')
    def test_query(self, mock_llm_client_class, config):
        """Test query processing"""
        from services.rag_service.rag_system import RAGServiceSystem
        
        # Mock LLM client
        mock_llm_client = MagicMock()
        mock_llm_client.chat = AsyncMock(return_value="Test answer")
        mock_llm_client_class.return_value = mock_llm_client
        
        # Mock retriever
        from langchain_core.documents import Document
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            Document(page_content="Test", metadata={})
        ]
        
        system = RAGServiceSystem(config)
        system.retriever = mock_retriever
        system.llm_client = mock_llm_client
        
        import asyncio
        result = asyncio.run(system.query("What is LoL?"))
        
        assert result == "Test answer"
        mock_llm_client.chat.assert_called_once()

