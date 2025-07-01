import os
from typing import Optional

from pydantic_settings import BaseSettings


def get_database_url() -> str:
    """Return appropriate database URL based on environment."""
    if os.getenv("TESTING") or os.getenv("PYTEST_CURRENT_TEST"):
        # Use SQLite for testing
        return "sqlite:///./test.db"
    else:
        # Use PostgreSQL for development and production
        return os.getenv("DATABASE_URL", "postgresql://rental_user:rental_password@localhost:5432/rental_db")


class Settings(BaseSettings):
    app_name: str = "Rental Manager API"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: str = "development"
    
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]
    
    # Logging configuration
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None
    enable_correlation_id: bool = True
    enable_performance_logging: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
    
    # Database URL will be determined dynamically
    @property
    def database_url(self) -> str:
        """Return appropriate database URL based on environment."""
        return get_database_url()

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


def get_settings() -> Settings:
    return Settings()