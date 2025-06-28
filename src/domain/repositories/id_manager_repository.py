from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..entities.id_manager import IdManager


class IdManagerRepository(ABC):
    @abstractmethod
    async def create(self, id_manager: IdManager) -> IdManager:
        """Create a new ID manager"""
        pass

    @abstractmethod
    async def get_by_id(self, manager_id: UUID) -> Optional[IdManager]:
        """Get ID manager by ID"""
        pass

    @abstractmethod
    async def get_by_prefix(self, prefix: str) -> Optional[IdManager]:
        """Get ID manager by prefix"""
        pass

    @abstractmethod
    async def get_or_create_by_prefix(self, prefix: str) -> IdManager:
        """Get existing ID manager by prefix or create new one"""
        pass

    @abstractmethod
    async def update(self, id_manager: IdManager) -> IdManager:
        """Update an existing ID manager"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[IdManager]:
        """Get all ID managers with pagination"""
        pass

    @abstractmethod
    async def delete(self, manager_id: UUID) -> bool:
        """Delete an ID manager (soft delete)"""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on ID manager service"""
        pass
