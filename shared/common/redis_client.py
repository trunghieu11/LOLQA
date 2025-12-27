"""Redis client utilities for caching and job queues"""
import json
import hashlib
from typing import Optional, Any, Dict
import redis
from redis.exceptions import RedisError
from shared.common.logging import logger


class RedisClient:
    """Redis client for caching and job queues"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize Redis client.
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(value)
            return self.client.setex(key, ttl, serialized)
        except (RedisError, TypeError) as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except RedisError as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def enqueue(self, queue_name: str, job: Dict[str, Any]) -> bool:
        """
        Add job to queue.
        
        Args:
            queue_name: Queue name
            job: Job data
            
        Returns:
            True if successful
        """
        if not self.client:
            return False
        
        try:
            serialized = json.dumps(job)
            self.client.lpush(queue_name, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.error(f"Error enqueueing job: {e}")
            return False
    
    def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """
        Get job from queue.
        
        Args:
            queue_name: Queue name
            timeout: Blocking timeout in seconds (0 = non-blocking)
            
        Returns:
            Job data or None
        """
        if not self.client:
            return None
        
        try:
            if timeout > 0:
                result = self.client.brpop(queue_name, timeout=timeout)
                if result:
                    _, serialized = result
                    return json.loads(serialized)
            else:
                serialized = self.client.rpop(queue_name)
                if serialized:
                    return json.loads(serialized)
            return None
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error dequeueing job: {e}")
            return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """Get queue length"""
        if not self.client:
            return 0
        
        try:
            return self.client.llen(queue_name)
        except RedisError as e:
            logger.error(f"Error getting queue length: {e}")
            return 0


def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from prefix and arguments.
    
    Args:
        prefix: Key prefix
        *args: Arguments to hash
        
    Returns:
        Cache key
    """
    key_string = ":".join(str(arg) for arg in args)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
    return f"{prefix}:{key_hash}"


def get_embedding_cache_key(text: str, model: str = "text-embedding-3-small") -> str:
    """Get cache key for embedding"""
    return get_cache_key("embedding", text, model)

