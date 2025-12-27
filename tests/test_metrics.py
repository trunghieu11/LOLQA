"""Tests for metrics utilities"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from shared.common.metrics import (
        http_requests_total,
        http_request_duration_seconds,
        cache_hits,
        cache_misses,
        get_metrics
    )
except ImportError:
    # Skip tests if prometheus_client is not installed
    pytest.skip("prometheus_client not installed", allow_module_level=True)


class TestMetrics:
    """Test Prometheus metrics"""
    
    def test_http_requests_counter(self):
        """Test HTTP requests counter"""
        http_requests_total.labels(method="GET", endpoint="/health", status="200").inc()
        http_requests_total.labels(method="GET", endpoint="/health", status="200").inc()
        
        # Get metrics
        metrics = get_metrics()
        assert b"http_requests_total" in metrics
    
    def test_http_request_duration_histogram(self):
        """Test HTTP request duration histogram"""
        http_request_duration_seconds.labels(method="POST", endpoint="/chat").observe(0.5)
        http_request_duration_seconds.labels(method="POST", endpoint="/chat").observe(1.0)
        
        # Get metrics
        metrics = get_metrics()
        assert b"http_request_duration_seconds" in metrics
    
    def test_cache_hits_counter(self):
        """Test cache hits counter"""
        cache_hits.labels(cache_type="embedding").inc()
        cache_hits.labels(cache_type="embedding").inc()
        
        # Get metrics
        metrics = get_metrics()
        assert b"cache_hits_total" in metrics
    
    def test_cache_misses_counter(self):
        """Test cache misses counter"""
        cache_misses.labels(cache_type="embedding").inc()
        
        # Get metrics
        metrics = get_metrics()
        assert b"cache_misses_total" in metrics
    
    def test_get_metrics_format(self):
        """Test metrics format"""
        metrics = get_metrics()
        
        # Should be valid Prometheus format
        assert isinstance(metrics, bytes)
        assert len(metrics) > 0
        # Should contain at least one metric
        assert b"#" in metrics or b"\n" in metrics

