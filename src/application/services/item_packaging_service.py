from typing import List, Optional

from ...domain.entities.item_packaging import ItemPackaging
from ...domain.repositories.item_packaging_repository import ItemPackagingRepository


class ItemPackagingService:
    def __init__(self, item_packaging_repository: ItemPackagingRepository):
        self.item_packaging_repository = item_packaging_repository

    async def create_item_packaging(
        self,
        name: str,
        label: str,
        unit: str,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> ItemPackaging:
        # Check if label already exists
        existing_packaging = await self.item_packaging_repository.get_by_label(label)
        if existing_packaging:
            raise ValueError(f"Item packaging with label '{label}' already exists")

        item_packaging = ItemPackaging(
            name=name,
            label=label,
            unit=unit,
            remarks=remarks,
            created_by=created_by,
        )
        return await self.item_packaging_repository.create(item_packaging)

    async def get_item_packaging_by_id(self, item_packaging_id: str) -> Optional[ItemPackaging]:
        return await self.item_packaging_repository.get_by_id(item_packaging_id)

    async def get_item_packaging_by_label(self, label: str) -> Optional[ItemPackaging]:
        return await self.item_packaging_repository.get_by_label(label)

    async def get_all_item_packagings(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[ItemPackaging]:
        return await self.item_packaging_repository.get_all(skip, limit, active_only)

    async def update_item_packaging(
        self,
        item_packaging_id: str,
        name: Optional[str] = None,
        label: Optional[str] = None,
        unit: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> ItemPackaging:
        item_packaging = await self.item_packaging_repository.get_by_id(item_packaging_id)
        if not item_packaging:
            raise ValueError(f"Item packaging with id {item_packaging_id} not found")

        # Check if new label conflicts with existing ones
        if label and label.upper() != item_packaging.label:
            existing_packaging = await self.item_packaging_repository.get_by_label(label)
            if existing_packaging:
                raise ValueError(f"Item packaging with label '{label}' already exists")

        if name:
            item_packaging.update_name(name)
        if label:
            item_packaging.update_label(label)
        if unit:
            item_packaging.update_unit(unit)
        if remarks is not None:  # Allow clearing remarks
            item_packaging.update_remarks(remarks)

        return await self.item_packaging_repository.update(item_packaging)

    async def deactivate_item_packaging(self, item_packaging_id: str) -> bool:
        item_packaging = await self.item_packaging_repository.get_by_id(item_packaging_id)
        if not item_packaging:
            raise ValueError(f"Item packaging with id {item_packaging_id} not found")

        item_packaging.deactivate()
        await self.item_packaging_repository.update(item_packaging)
        return True

    async def activate_item_packaging(self, item_packaging_id: str) -> bool:
        item_packaging = await self.item_packaging_repository.get_by_id(item_packaging_id)
        if not item_packaging:
            raise ValueError(f"Item packaging with id {item_packaging_id} not found")

        item_packaging.activate()
        await self.item_packaging_repository.update(item_packaging)
        return True

    async def search_item_packagings_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[ItemPackaging]:
        return await self.item_packaging_repository.search_by_name(name, skip, limit)
