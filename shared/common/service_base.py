"""Base utilities for FastAPI services"""
from typing import Optional
from fastapi import FastAPI, HTTPException
from shared.common.middleware import setup_cors_middleware, setup_metrics_middleware
from shared.common.models import HealthResponse


class ServiceBase:
    """Base class for FastAPI services with common setup"""
    
    def __init__(
        self,
        app: FastAPI,
        service_name: str,
        service_version: str,
        enable_cors: bool = True,
        enable_metrics: bool = True,
        cors_origins: Optional[list[str]] = None
    ):
        """
        Initialize service base.
        
        Args:
            app: FastAPI application instance
            service_name: Name of the service
            service_version: Version of the service
            enable_cors: Whether to enable CORS middleware
            enable_metrics: Whether to enable metrics middleware
            cors_origins: CORS allowed origins (default: ["*"])
        """
        self.app = app
        self.service_name = service_name
        self.service_version = service_version
        
        # Setup middleware
        if enable_cors:
            setup_cors_middleware(app, cors_origins)
        
        if enable_metrics:
            setup_metrics_middleware(app)
        
        # Register health check endpoint
        self._register_health_check()
    
    def _register_health_check(self) -> None:
        """Register health check endpoint"""
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            return HealthResponse(
                status="healthy",
                service=self.service_name,
                version=self.service_version
            )

