from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.inventory_item_master import InventoryItemMaster


class InventoryItemMasterRepository(ABC):
    @abstractmethod
    async def save(self, inventory_item: InventoryItemMaster) -> InventoryItemMaster:
        pass
    
    @abstractmethod
    async def find_by_id(self, inventory_item_id: UUID) -> Optional[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def find_by_sku(self, sku: str) -> Optional[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def find_by_subcategory(self, subcategory_id: UUID, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def find_by_tracking_type(self, tracking_type: str, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def find_consumables(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def search(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[InventoryItemMaster]:
        pass
    
    @abstractmethod
    async def update(self, inventory_item: InventoryItemMaster) -> InventoryItemMaster:
        pass
    
    @abstractmethod
    async def delete(self, inventory_item_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def exists_by_sku(self, sku: str, exclude_id: Optional[UUID] = None) -> bool:
        pass
    
    @abstractmethod
    async def exists_by_name(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        pass
    
    @abstractmethod
    async def count(self) -> int:
        pass
    
    @abstractmethod
    async def count_by_subcategory(self, subcategory_id: UUID) -> int:
        pass
    
    @abstractmethod
    async def update_quantity(self, inventory_item_id: UUID, new_quantity: int) -> bool:
        pass