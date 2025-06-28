from functools import lru_cache

from ...infrastructure.database.base import DatabaseManager
from .settings import get_settings


@lru_cache()
def get_database_manager() -> DatabaseManager:
    settings = get_settings()
    return DatabaseManager(settings.database_url)


def get_db_session():
    db_manager = get_database_manager()
    session = db_manager.SessionLocal()
    try:
        yield session
    finally:
        session.close()