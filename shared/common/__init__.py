"""Shared common utilities for microservices"""
from shared.common.logging import setup_logger, logger
from shared.common.config import get_config
from shared.common.models import (
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    HealthResponse,
    PipelineJobRequest,
    PipelineJobResponse,
    ChatMessage
)
from shared.common.redis_client import RedisClient, get_cache_key, get_embedding_cache_key
from shared.common.db_client import DatabaseClient, get_db_client
from shared.common.metrics import get_metrics, http_requests_total, http_request_duration_seconds

__all__ = [
    "setup_logger",
    "logger",
    "get_config",
    "ChatRequest",
    "ChatResponse",
    "EmbeddingRequest",
    "EmbeddingResponse",
    "RAGQueryRequest",
    "RAGQueryResponse",
    "HealthResponse",
    "PipelineJobRequest",
    "PipelineJobResponse",
    "ChatMessage",
    "RedisClient",
    "get_cache_key",
    "get_embedding_cache_key",
    "DatabaseClient",
    "get_db_client",
    "get_metrics",
    "http_requests_total",
    "http_request_duration_seconds",
]

