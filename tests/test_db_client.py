"""Tests for database client utilities"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from shared.common.db_client import DatabaseClient, get_db_client


class TestDatabaseClient:
    """Test database client"""
    
    @pytest.fixture
    def mock_connection(self):
        """Mock database connection"""
        mock = MagicMock()
        mock.cursor.return_value.__enter__.return_value = MagicMock()
        mock.cursor.return_value.__exit__.return_value = None
        mock.commit = MagicMock()
        mock.rollback = MagicMock()
        return mock
    
    @pytest.fixture
    def mock_pool(self, mock_connection):
        """Mock connection pool"""
        mock = MagicMock()
        mock.getconn.return_value = mock_connection
        mock.putconn = MagicMock()
        return mock
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_init_success(self, mock_pool_class, mock_pool):
        """Test successful database initialization"""
        mock_pool_class.return_value = mock_pool
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        assert client.pool is not None
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_execute_query(self, mock_pool_class, mock_pool, mock_connection):
        """Test executing SELECT query"""
        from psycopg2.extras import RealDictRow
        
        mock_pool_class.return_value = mock_pool
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            RealDictRow([('id', 1), ('name', 'test')])
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        results = client.execute_query("SELECT * FROM test WHERE id = %s", (1,))
        
        assert len(results) == 1
        assert results[0]['id'] == 1
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_execute_update(self, mock_pool_class, mock_pool, mock_connection):
        """Test executing INSERT/UPDATE query"""
        mock_pool_class.return_value = mock_pool
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        result = client.execute_update("INSERT INTO test (name) VALUES (%s)", ("test",))
        
        assert result is True
        mock_cursor.execute.assert_called_once()
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_create_pipeline_job(self, mock_pool_class, mock_pool, mock_connection):
        """Test creating pipeline job"""
        mock_pool_class.return_value = mock_pool
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        result = client.create_pipeline_job("job123", "queued", "Job queued")
        
        assert result is True
        mock_cursor.execute.assert_called_once()
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_update_pipeline_job(self, mock_pool_class, mock_pool, mock_connection):
        """Test updating pipeline job"""
        mock_pool_class.return_value = mock_pool
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        result = client.update_pipeline_job("job123", "completed", "Done", {"docs": 10})
        
        assert result is True
        mock_cursor.execute.assert_called_once()
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_get_pipeline_job(self, mock_pool_class, mock_pool, mock_connection):
        """Test getting pipeline job"""
        from psycopg2.extras import RealDictRow
        
        mock_pool_class.return_value = mock_pool
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            RealDictRow([('job_id', 'job123'), ('status', 'running')])
        ]
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        job = client.get_pipeline_job("job123")
        
        assert job is not None
        assert job['job_id'] == 'job123'
        assert job['status'] == 'running'
    
    @patch('shared.common.db_client.ThreadedConnectionPool')
    def test_log_query(self, mock_pool_class, mock_pool, mock_connection):
        """Test logging query"""
        mock_pool_class.return_value = mock_pool
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
        
        client = DatabaseClient("postgresql://user:pass@localhost:5432/db")
        result = client.log_query("What is LoL?", "Answer", "rag-service", 150, {"k": 3})
        
        assert result is True
        mock_cursor.execute.assert_called_once()


class TestGetDbClient:
    """Test get_db_client function"""
    
    @patch('shared.common.db_client.DatabaseClient')
    def test_get_db_client_singleton(self, mock_client_class):
        """Test that get_db_client returns singleton"""
        from shared.common.db_client import _db_client
        import shared.common.db_client as db_module
        
        # Reset singleton
        db_module._db_client = None
        
        client1 = get_db_client()
        client2 = get_db_client()
        
        # Should return same instance
        assert client1 is client2

