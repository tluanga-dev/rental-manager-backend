from typing import List, Optional


from ...domain.entities.item_packaging import ItemPackaging
from ..services.item_packaging_service import ItemPackagingService


class ItemPackagingUseCases:
    def __init__(self, item_packaging_service: ItemPackagingService):
        self.item_packaging_service = item_packaging_service

    async def create_item_packaging(
        self,
        name: str,
        label: str,
        unit: str,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ItemPackaging:
        """Create a new item packaging"""
        return await self.item_packaging_service.create_item_packaging(
            name=name,
            label=label,
            unit=unit,
            remarks=remarks,
            created_by=created_by,
        )

    async def get_item_packaging(self, item_packaging_id: str) -> Optional[ItemPackaging]:
        """Get item packaging by ID"""
        return await self.item_packaging_service.get_item_packaging_by_id(item_packaging_id)

    async def get_item_packaging_by_label(self, label: str) -> Optional[ItemPackaging]:
        """Get item packaging by label"""
        return await self.item_packaging_service.get_item_packaging_by_label(label)

    async def list_item_packagings(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[ItemPackaging]:
        """List all item packagings with pagination"""
        return await self.item_packaging_service.get_all_item_packagings(skip, limit, active_only)

    async def update_item_packaging(
        self,
        item_packaging_id: str,
        name: Optional[str] = None,
        label: Optional[str] = None,
        unit: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> ItemPackaging:
        """Update an existing item packaging"""
        return await self.item_packaging_service.update_item_packaging(
            item_packaging_id=item_packaging_id,
            name=name,
            label=label,
            unit=unit,
            remarks=remarks,
        )

    async def deactivate_item_packaging(self, item_packaging_id: str) -> bool:
        """Deactivate an item packaging (soft delete)"""
        return await self.item_packaging_service.deactivate_item_packaging(item_packaging_id)

    async def activate_item_packaging(self, item_packaging_id: str) -> bool:
        """Activate an item packaging"""
        return await self.item_packaging_service.activate_item_packaging(item_packaging_id)

    async def search_item_packagings(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[ItemPackaging]:
        """Search item packagings by name"""
        return await self.item_packaging_service.search_item_packagings_by_name(name, skip, limit)
