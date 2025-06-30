from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.router import api_router
from .core.config.database import get_database_manager
from .core.config.logging import LogConfig, configure_logging, get_logger
from .core.config.settings import get_settings
from .core.middleware import (
    CorrelationIDMiddleware,
    PerformanceMonitoringMiddleware,
    RequestLoggingMiddleware,
)

settings = get_settings()

# Configure logging
log_config = LogConfig(
    log_level=settings.log_level,
    log_format=settings.log_format,
    log_file=settings.log_file,
    enable_correlation_id=settings.enable_correlation_id,
    enable_performance_logging=settings.enable_performance_logging,
)
configure_logging(log_config)

# Get application logger
logger = get_logger("main")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# Add custom middleware
app.add_middleware(CorrelationIDMiddleware)
if settings.enable_performance_logging:
    app.add_middleware(PerformanceMonitoringMiddleware, slow_request_threshold=1.0)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Main API router for /api/v1
app.include_router(api_router)

# New router for /api prefix
api_prefix_router = APIRouter(prefix="/api")

@api_prefix_router.get("/health")
async def api_health_check():
    return {"status": "healthy", "service": settings.app_name, "path": "/api/health"}

app.include_router(api_prefix_router)


@app.on_event("startup")
async def startup_event():
    logger.info("application_starting", app_name=settings.app_name, version=settings.app_version)
    db_manager = get_database_manager()
    db_manager.create_tables()
    logger.info("application_started", environment=settings.environment)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.app_name}


def get_application() -> FastAPI:
    return app