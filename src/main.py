from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.router import api_router
from .core.config.database import get_database_manager
from .core.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

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
    db_manager = get_database_manager()
    db_manager.create_tables()


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