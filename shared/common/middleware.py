"""Common middleware for FastAPI services"""
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from shared.common.metrics import (
    http_requests_total,
    http_request_duration_seconds
)


def setup_cors_middleware(app: FastAPI, allow_origins: list[str] = None) -> None:
    """
    Setup CORS middleware for FastAPI app.
    
    Args:
        app: FastAPI application instance
        allow_origins: List of allowed origins (default: ["*"])
    """
    if allow_origins is None:
        allow_origins = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def metrics_middleware(request: Request, call_next: Callable) -> Response:
    """
    Middleware to track Prometheus metrics for HTTP requests.
    
    Args:
        request: FastAPI request object
        call_next: Next middleware/handler in chain
        
    Returns:
        Response object
    """
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Track request metrics
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response


def setup_metrics_middleware(app: FastAPI) -> None:
    """
    Setup metrics middleware for FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.middleware("http")(metrics_middleware)

