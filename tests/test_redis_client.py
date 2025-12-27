"""Tests for Redis client utilities"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from shared.common.redis_client import RedisClient, get_cache_key, get_embedding_cache_key


class TestRedisClient:
    """Test Redis client"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis connection"""
        mock = MagicMock()
        mock.ping.return_value = True
        mock.get.return_value = None
        mock.setex.return_value = True
        mock.delete.return_value = 1
        mock.lpush.return_value = 1
        mock.rpop.return_value = None
        mock.brpop.return_value = None
        mock.llen.return_value = 0
        return mock
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_init_success(self, mock_from_url, mock_redis):
        """Test successful Redis initialization"""
        mock_from_url.return_value = mock_redis
        
        client = RedisClient("redis://localhost:6379/0")
        assert client.client is not None
        mock_redis.ping.assert_called_once()
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_init_failure(self, mock_from_url):
        """Test Redis initialization failure"""
        import redis.exceptions
        mock_from_url.side_effect = redis.exceptions.ConnectionError("Connection failed")
        
        client = RedisClient("redis://localhost:6379/0")
        assert client.client is None
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_get_cache_hit(self, mock_from_url, mock_redis):
        """Test cache hit"""
        import json
        mock_from_url.return_value = mock_redis
        mock_redis.get.return_value = json.dumps({"key": "value"})
        
        client = RedisClient("redis://localhost:6379/0")
        result = client.get("test_key")
        
        assert result == {"key": "value"}
        mock_redis.get.assert_called_once_with("test_key")
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_get_cache_miss(self, mock_from_url, mock_redis):
        """Test cache miss"""
        mock_from_url.return_value = mock_redis
        mock_redis.get.return_value = None
        
        client = RedisClient("redis://localhost:6379/0")
        result = client.get("test_key")
        
        assert result is None
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_set_cache(self, mock_from_url, mock_redis):
        """Test setting cache"""
        import json
        mock_from_url.return_value = mock_redis
        
        client = RedisClient("redis://localhost:6379/0")
        result = client.set("test_key", {"key": "value"}, ttl=3600)
        
        assert result is True
        mock_redis.setex.assert_called_once()
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_delete_cache(self, mock_from_url, mock_redis):
        """Test deleting from cache"""
        mock_from_url.return_value = mock_redis
        
        client = RedisClient("redis://localhost:6379/0")
        result = client.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_enqueue(self, mock_from_url, mock_redis):
        """Test enqueueing job"""
        import json
        mock_from_url.return_value = mock_redis
        
        client = RedisClient("redis://localhost:6379/0")
        result = client.enqueue("test_queue", {"job_id": "123", "data": "test"})
        
        assert result is True
        mock_redis.lpush.assert_called_once()
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_dequeue(self, mock_from_url, mock_redis):
        """Test dequeueing job"""
        import json
        mock_from_url.return_value = mock_redis
        mock_redis.rpop.return_value = json.dumps({"job_id": "123", "data": "test"})
        
        client = RedisClient("redis://localhost:6379/0")
        result = client.dequeue("test_queue")
        
        assert result == {"job_id": "123", "data": "test"}
        mock_redis.rpop.assert_called_once_with("test_queue")
    
    @patch('shared.common.redis_client.redis.from_url')
    def test_get_queue_length(self, mock_from_url, mock_redis):
        """Test getting queue length"""
        mock_from_url.return_value = mock_redis
        mock_redis.llen.return_value = 5
        
        client = RedisClient("redis://localhost:6379/0")
        length = client.get_queue_length("test_queue")
        
        assert length == 5
        mock_redis.llen.assert_called_once_with("test_queue")


class TestCacheKeyGeneration:
    """Test cache key generation"""
    
    def test_get_cache_key(self):
        """Test cache key generation"""
        key = get_cache_key("prefix", "arg1", "arg2")
        assert key.startswith("prefix:")
        assert len(key) > len("prefix:")
    
    def test_get_embedding_cache_key(self):
        """Test embedding cache key generation"""
        key1 = get_embedding_cache_key("test text", "model1")
        key2 = get_embedding_cache_key("test text", "model1")
        key3 = get_embedding_cache_key("test text", "model2")
        
        # Same text and model should produce same key
        assert key1 == key2
        # Different model should produce different key
        assert key1 != key3

