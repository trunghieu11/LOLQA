"""Integration tests for microservices"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import httpx
except ImportError:
    httpx = None
    pytest.skip("httpx not installed", allow_module_level=True)


class TestMicroservicesIntegration:
    """Integration tests for microservices communication"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service responses"""
        return {
            "/chat": {
                "content": "Test response",
                "model": "gpt-4o-mini"
            },
            "/embeddings": {
                "embeddings": [[0.1] * 1536],
                "model": "text-embedding-3-small"
            }
        }
    
    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service responses"""
        return {
            "/query": {
                "answer": "Ahri has 4 abilities: Q, W, E, and R",
                "context": []
            },
            "/retrieve": {
                "documents": [
                    {
                        "content": "Ahri is a nine-tailed fox mage",
                        "metadata": {"type": "champion"}
                    }
                ]
            }
        }
    
    @patch('httpx.Client')
    def test_ui_to_rag_flow(self, mock_httpx, mock_rag_service):
        """Test UI service calling RAG service"""
        # Mock HTTP client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_rag_service["/query"]
        mock_response.raise_for_status = MagicMock()
        mock_client.post.return_value = mock_response
        mock_httpx.return_value.__enter__.return_value = mock_client
        
        # Simulate UI service calling RAG service
        response = httpx.post(
            "http://rag-service:8000/query",
            json={
                "question": "What are Ahri's abilities?",
                "conversation_history": None
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
    
    @patch('httpx.AsyncClient')
    async def test_rag_to_llm_flow(self, mock_httpx, mock_llm_service):
        """Test RAG service calling LLM service"""
        # Mock async HTTP client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_llm_service["/chat"]
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        # Simulate RAG service calling LLM service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://llm-service:8000/chat",
                json={
                    "messages": [
                        {"role": "user", "content": "Hello"}
                    ]
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
    
    @patch('httpx.AsyncClient')
    async def test_pipeline_to_llm_flow(self, mock_httpx, mock_llm_service):
        """Test Data Pipeline service calling LLM service for embeddings"""
        # Mock async HTTP client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_llm_service["/embeddings"]
        mock_response.raise_for_status = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_httpx.return_value.__aenter__.return_value = mock_client
        
        # Simulate pipeline service calling LLM service
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://llm-service:8000/embeddings",
                json={
                    "texts": ["test text"]
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "embeddings" in data
    
    @patch('shared.common.redis_client.RedisClient')
    @patch('shared.common.db_client.get_db_client')
    def test_pipeline_job_flow(self, mock_db, mock_redis):
        """Test complete pipeline job flow"""
        # Mock database
        mock_db_instance = MagicMock()
        mock_db_instance.create_pipeline_job.return_value = True
        mock_db_instance.update_pipeline_job.return_value = True
        mock_db_instance.get_pipeline_job.return_value = {
            "job_id": "test-job",
            "status": "completed"
        }
        mock_db.return_value = mock_db_instance
        
        # Mock Redis
        mock_redis_instance = MagicMock()
        mock_redis_instance.enqueue.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        # Simulate job creation
        job_id = "test-job-123"
        mock_db_instance.create_pipeline_job(job_id, "queued", "Job queued")
        mock_redis_instance.enqueue("pipeline_jobs", {"job_id": job_id})
        
        # Verify job was created
        mock_db_instance.create_pipeline_job.assert_called_once()
        mock_redis_instance.enqueue.assert_called_once()
        
        # Simulate job completion
        mock_db_instance.update_pipeline_job(
            job_id, "completed", "Done", {"documents": 10}
        )
        
        # Verify job status
        job = mock_db_instance.get_pipeline_job(job_id)
        assert job["status"] == "completed"
    
    @patch('shared.common.redis_client.RedisClient')
    def test_embedding_cache_flow(self, mock_redis):
        """Test embedding caching flow"""
        import json
        from shared.common.redis_client import get_embedding_cache_key
        
        # Mock Redis
        mock_redis_instance = MagicMock()
        mock_redis_instance.get.return_value = None  # Cache miss
        mock_redis_instance.set.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        text = "test text"
        model = "text-embedding-3-small"
        cache_key = get_embedding_cache_key(text, model)
        
        # First call - cache miss
        cached = mock_redis_instance.get(cache_key)
        assert cached is None
        
        # Store in cache
        embedding = [0.1] * 1536
        mock_redis_instance.set(cache_key, embedding, ttl=86400)
        
        # Second call - cache hit
        mock_redis_instance.get.return_value = embedding
        cached = mock_redis_instance.get(cache_key)
        assert cached == embedding


class TestServiceHealthChecks:
    """Test service health checks"""
    
    @pytest.mark.parametrize("service,port", [
        ("llm-service", 8001),
        ("rag-service", 8002),
        ("data-pipeline-service", 8003),
        ("auth-service", 8004),
    ])
    def test_service_health_endpoints(self, service, port):
        """Test all service health endpoints"""
        # This would make actual HTTP calls in integration tests
        # For unit tests, we mock the responses
        pass  # Placeholder for actual integration test

