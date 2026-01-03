"""Common error handling utilities for FastAPI services"""
from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException
from shared.common.logging import logger


def handle_service_errors(
    default_status: int = 500,
    log_error: bool = True
) -> Callable:
    """
    Decorator to handle exceptions in service endpoints.
    
    Args:
        default_status: Default HTTP status code for errors
        log_error: Whether to log errors
        
    Example:
        @handle_service_errors()
        async def my_endpoint():
            # Your code here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Error in {func.__name__}: {e}",
                        exc_info=True
                    )
                raise HTTPException(
                    status_code=default_status,
                    detail=str(e)
                )
        return wrapper
    return decorator

