from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.warehouse import Warehouse


class WarehouseRepository(ABC):
    @abstractmethod
    async def create(self, warehouse: Warehouse) -> Warehouse:
        """Create a new warehouse"""
        pass

    @abstractmethod
    async def get_by_id(self, warehouse_id: UUID) -> Optional[Warehouse]:
        """Get warehouse by ID"""
        pass

    @abstractmethod
    async def get_by_label(self, label: str) -> Optional[Warehouse]:
        """Get warehouse by label"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Warehouse]:
        """Get all warehouses with pagination"""
        pass

    @abstractmethod
    async def update(self, warehouse: Warehouse) -> Warehouse:
        """Update an existing warehouse"""
        pass

    @abstractmethod
    async def delete(self, warehouse_id: UUID) -> bool:
        """Delete a warehouse (soft delete)"""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Warehouse]:
        """Search warehouses by name"""
        pass
