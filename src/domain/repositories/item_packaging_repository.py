from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.item_packaging import ItemPackaging


class ItemPackagingRepository(ABC):
    @abstractmethod
    async def create(self, item_packaging: ItemPackaging) -> ItemPackaging:
        """Create a new item packaging"""
        pass

    @abstractmethod
    async def get_by_id(self, item_packaging_id: UUID) -> Optional[ItemPackaging]:
        """Get item packaging by ID"""
        pass

    @abstractmethod
    async def get_by_label(self, label: str) -> Optional[ItemPackaging]:
        """Get item packaging by label"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[ItemPackaging]:
        """Get all item packagings with pagination"""
        pass

    @abstractmethod
    async def update(self, item_packaging: ItemPackaging) -> ItemPackaging:
        """Update an existing item packaging"""
        pass

    @abstractmethod
    async def delete(self, item_packaging_id: UUID) -> bool:
        """Delete an item packaging (soft delete)"""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[ItemPackaging]:
        """Search item packagings by name"""
        pass
