"""Tests for Data Pipeline Service"""
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
    pipeline_module = import_service_module("data-pipeline-service", "main")
    app = pipeline_module.app
    
    from shared.common.config import DataPipelineConfig
except (ImportError, AttributeError) as e:
    pytest.skip(f"Could not import data pipeline service: {e}", allow_module_level=True)


class TestDataPipelineServiceAPI:
    """Test Data Pipeline Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @patch('services.data_pipeline_service.main.DataPipeline')
    def test_health_check(self, mock_pipeline, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "data-pipeline-service"
    
    @patch('services.data_pipeline_service.main.pipeline')
    @patch('services.data_pipeline_service.main.db_client')
    @patch('services.data_pipeline_service.main.redis_client')
    def test_ingest(self, mock_redis, mock_db, mock_pipeline, client):
        """Test data ingestion endpoint"""
        import uuid
        
        # Mock pipeline
        mock_pipeline.run = AsyncMock(return_value={
            "documents": 10,
            "chunks": 50,
            "status": "success"
        })
        
        # Mock database
        mock_db.create_pipeline_job.return_value = True
        
        # Mock Redis
        mock_redis.enqueue.return_value = True
        
        response = client.post(
            "/ingest",
            json={
                "force_refresh": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"
    
    @patch('services.data_pipeline_service.main.db_client')
    def test_get_job_status(self, mock_db, client):
        """Test get job status endpoint"""
        mock_db.get_pipeline_job.return_value = {
            "job_id": "test-job",
            "status": "running",
            "message": "Processing..."
        }
        
        response = client.get("/status/test-job")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-job"
        assert data["status"] == "running"
    
    @patch('services.data_pipeline_service.main.db_client')
    def test_get_job_status_not_found(self, mock_db, client):
        """Test get job status when job not found"""
        mock_db.get_pipeline_job.return_value = None
        
        response = client.get("/status/nonexistent-job")
        
        assert response.status_code == 404
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]


class TestDataPipeline:
    """Test Data Pipeline"""
    
    @pytest.fixture
    def config(self):
        """Create test config"""
        return DataPipelineConfig(
            service_name="data-pipeline-service",
            llm_service_url="http://llm-service:8000",
            vector_db_path="./test_chroma_db"
        )
    
    @patch('services.data_pipeline_service.pipeline.LoLDataCollector')
    @patch('services.data_pipeline_service.pipeline.RecursiveCharacterTextSplitter')
    @patch('services.data_pipeline_service.pipeline.Chroma')
    @patch('services.data_pipeline_service.pipeline.OpenAIEmbeddings')
    def test_run_pipeline(self, mock_embeddings, mock_chroma, mock_splitter, mock_collector, config):
        """Test pipeline execution"""
        from services.data_pipeline_service.pipeline import DataPipeline
        from langchain_core.documents import Document
        
        # Mock data collector
        mock_collector_instance = MagicMock()
        mock_collector_instance.get_documents.return_value = [
            Document(page_content="Test", metadata={"type": "champion"})
        ]
        mock_collector.return_value = mock_collector_instance
        
        # Mock text splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.split_documents.return_value = [
            Document(page_content="Test chunk", metadata={})
        ]
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock vector store
        mock_vectorstore = MagicMock()
        mock_chroma.from_documents.return_value = mock_vectorstore
        
        pipeline = DataPipeline(config)
        
        import asyncio
        result = asyncio.run(pipeline.run())
        
        assert result["status"] == "success"
        assert "documents" in result
        assert "chunks" in result

