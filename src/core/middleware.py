"""
Middleware for the FastAPI application.

This module contains middleware for correlation ID tracking,
request/response logging, and performance monitoring.
"""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config.logging import get_logger, sanitize_sensitive_data, set_correlation_id

logger = get_logger("middleware")


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to all requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        
        # Set correlation ID in context
        set_correlation_id(correlation_id)
        
        # Add correlation ID to response headers
        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and responses."""
    
    def __init__(self, app, exclude_paths: set[str] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or {"/health", "/docs", "/openapi.json", "/favicon.ico"}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        start_time = time.time()
        
        # Log incoming request
        request_data = {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": sanitize_sensitive_data(dict(request.headers)),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
        
        logger.info("request_started", **request_data)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            response_data = {
                "status_code": response.status_code,
                "process_time_seconds": process_time,
                "process_time_ms": process_time * 1000,
                "response_headers": sanitize_sensitive_data(dict(response.headers)),
            }
            
            if response.status_code >= 400:
                logger.warning("request_completed_with_error", **{**request_data, **response_data})
            else:
                logger.info("request_completed", **{**request_data, **response_data})
            
            # Add processing time header
            response.headers["x-process-time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Calculate processing time for failed requests
            process_time = time.time() - start_time
            
            logger.error(
                "request_failed",
                **request_data,
                error_type=type(e).__name__,
                error_message=str(e),
                process_time_seconds=process_time,
                process_time_ms=process_time * 1000,
            )
            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor API performance and add metrics."""
    
    def __init__(self, app, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log slow requests
            if process_time > self.slow_request_threshold:
                logger.warning(
                    "slow_request_detected",
                    method=request.method,
                    path=request.url.path,
                    process_time_seconds=process_time,
                    process_time_ms=process_time * 1000,
                    threshold_seconds=self.slow_request_threshold,
                )
            
            # Add performance metrics to response headers
            response.headers["x-response-time"] = f"{process_time:.3f}s"
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            logger.error(
                "request_exception",
                method=request.method,
                path=request.url.path,
                error_type=type(e).__name__,
                error_message=str(e),
                process_time_seconds=process_time,
                process_time_ms=process_time * 1000,
            )
            raise