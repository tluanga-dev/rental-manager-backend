"""
Centralized logging configuration for the rental management system.

This module provides structured JSON logging with correlation IDs,
performance metrics, and environment-specific configuration.
"""

import logging
import logging.config
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any, Dict, Optional

import structlog
from pydantic import BaseModel
from structlog.typing import FilteringBoundLogger

# Context variable for correlation ID tracking across async operations
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


class LogConfig(BaseModel):
    """Logging configuration model."""
    
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    log_file: Optional[str] = None
    enable_correlation_id: bool = True
    enable_performance_logging: bool = True
    
    class Config:
        case_sensitive = False


def add_correlation_id(logger: FilteringBoundLogger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add correlation ID to log events."""
    correlation_id = correlation_id_var.get()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict


def add_timestamp(logger: FilteringBoundLogger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add ISO timestamp to log events."""
    event_dict["timestamp"] = time.time()
    return event_dict


def add_logger_name(logger: FilteringBoundLogger, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add logger name to log events."""
    event_dict["logger"] = logger.name if hasattr(logger, 'name') else "unknown"
    return event_dict


def configure_logging(config: LogConfig) -> None:
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.log_level.upper()),
    )
    
    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_correlation_id,
        add_timestamp,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    # Add appropriate renderer based on format
    if config.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> FilteringBoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for the current context."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID."""
    return correlation_id_var.get()


class LoggingMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> FilteringBoundLogger:
        """Get a logger instance bound to this class."""
        return get_logger(self.__class__.__name__)


class PerformanceLogger:
    """Context manager for performance logging."""
    
    def __init__(self, operation: str, logger: Optional[FilteringBoundLogger] = None):
        self.operation = operation
        self.logger = logger or get_logger("performance")
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info("operation_started", operation=self.operation)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.time() - self.start_time
            
            if exc_type is None:
                self.logger.info(
                    "operation_completed",
                    operation=self.operation,
                    duration_seconds=duration,
                    duration_ms=duration * 1000
                )
            else:
                self.logger.error(
                    "operation_failed",
                    operation=self.operation,
                    duration_seconds=duration,
                    duration_ms=duration * 1000,
                    error_type=exc_type.__name__ if exc_type else None,
                    error_message=str(exc_val) if exc_val else None
                )


def log_function_call(logger: Optional[FilteringBoundLogger] = None):
    """Decorator to log function calls with performance metrics."""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_logger = logger or get_logger(func.__module__)
            operation_name = f"{func.__module__}.{func.__name__}"
            
            with PerformanceLogger(operation_name, func_logger):
                func_logger.debug(
                    "function_called",
                    function=func.__name__,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys())
                )
                
                try:
                    result = func(*args, **kwargs)
                    func_logger.debug("function_completed", function=func.__name__)
                    return result
                except Exception as e:
                    func_logger.error(
                        "function_error",
                        function=func.__name__,
                        error_type=type(e).__name__,
                        error_message=str(e)
                    )
                    raise
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    return decorator


def sanitize_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove or mask sensitive data from log entries."""
    sensitive_keys = {
        "password", "token", "secret", "key", "authorization",
        "credit_card", "ssn", "social_security"
    }
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_sensitive_data(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized