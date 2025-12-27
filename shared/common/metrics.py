"""Prometheus metrics utilities"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
from typing import Optional
import time
from functools import wraps


# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections',
    ['service']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

queue_length = Gauge(
    'queue_length',
    'Number of items in queue',
    ['queue_name']
)


def track_request_metrics(func):
    """Decorator to track request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        method = kwargs.get('method', 'GET')
        endpoint = kwargs.get('endpoint', 'unknown')
        
        try:
            response = await func(*args, **kwargs)
            status = '200' if hasattr(response, 'status_code') else '200'
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(time.time() - start_time)
            return response
        except Exception as e:
            http_requests_total.labels(method=method, endpoint=endpoint, status='500').inc()
            raise
    
    return wrapper


def get_metrics():
    """Get Prometheus metrics"""
    return generate_latest(REGISTRY)

