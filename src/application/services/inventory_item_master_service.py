from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from ...domain.entities.inventory_item_master import InventoryItemMaster
from ...domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from ..use_cases.inventory_item_master_use_cases import (
    CreateInventoryItemMasterUseCase,
    GetInventoryItemMasterUseCase,
    GetInventoryItemMasterBySkuUseCase,
    UpdateInventoryItemMasterUseCase,
    DeleteInventoryItemMasterUseCase,
    ListInventoryItemMastersUseCase,
    ListInventoryItemMastersBySubcategoryUseCase,
    ListInventoryItemMastersByTrackingTypeUseCase,
    ListConsumableInventoryItemMastersUseCase,
    SearchInventoryItemMastersUseCase,
    UpdateInventoryItemMasterQuantityUseCase,
    UpdateInventoryItemMasterDimensionsUseCase,
)


class InventoryItemMasterService:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository
        self.create_use_case = CreateInventoryItemMasterUseCase(repository)
        self.get_use_case = GetInventoryItemMasterUseCase(repository)
        self.get_by_sku_use_case = GetInventoryItemMasterBySkuUseCase(repository)
        self.update_use_case = UpdateInventoryItemMasterUseCase(repository)
        self.delete_use_case = DeleteInventoryItemMasterUseCase(repository)
        self.list_use_case = ListInventoryItemMastersUseCase(repository)
        self.list_by_subcategory_use_case = ListInventoryItemMastersBySubcategoryUseCase(repository)
        self.list_by_tracking_type_use_case = ListInventoryItemMastersByTrackingTypeUseCase(repository)
        self.list_consumables_use_case = ListConsumableInventoryItemMastersUseCase(repository)
        self.search_use_case = SearchInventoryItemMastersUseCase(repository)
        self.update_quantity_use_case = UpdateInventoryItemMasterQuantityUseCase(repository)
        self.update_dimensions_use_case = UpdateInventoryItemMasterDimensionsUseCase(repository)

    async def create_inventory_item_master(
        self,
        name: str,
        sku: str,
        item_sub_category_id: UUID,
        unit_of_measurement_id: UUID,
        tracking_type: str,
        is_consumable: bool = False,
        description: Optional[str] = None,
        contents: Optional[str] = None,
        packaging_id: Optional[UUID] = None,
        brand: Optional[str] = None,
        manufacturer_part_number: Optional[str] = None,
        product_id: Optional[str] = None,
        weight: Optional[Decimal] = None,
        length: Optional[Decimal] = None,
        width: Optional[Decimal] = None,
        height: Optional[Decimal] = None,
        renting_period: int = 1,
        quantity: int = 0,
        created_by: Optional[str] = None
    ) -> InventoryItemMaster:
        return await self.create_use_case.execute(
            name=name,
            sku=sku,
            item_sub_category_id=item_sub_category_id,
            unit_of_measurement_id=unit_of_measurement_id,
            tracking_type=tracking_type,
            is_consumable=is_consumable,
            description=description,
            contents=contents,
            packaging_id=packaging_id,
            brand=brand,
            manufacturer_part_number=manufacturer_part_number,
            product_id=product_id,
            weight=weight,
            length=length,
            width=width,
            height=height,
            renting_period=renting_period,
            quantity=quantity,
            created_by=created_by
        )

    async def get_inventory_item_master(self, inventory_item_id: UUID) -> Optional[InventoryItemMaster]:
        return await self.get_use_case.execute(inventory_item_id)

    async def get_inventory_item_master_by_sku(self, sku: str) -> Optional[InventoryItemMaster]:
        return await self.get_by_sku_use_case.execute(sku)

    async def update_inventory_item_master(
        self,
        inventory_item_id: UUID,
        name: Optional[str] = None,
        sku: Optional[str] = None,
        description: Optional[str] = None,
        contents: Optional[str] = None,
        item_sub_category_id: Optional[UUID] = None,
        unit_of_measurement_id: Optional[UUID] = None,
        packaging_id: Optional[UUID] = None,
        tracking_type: Optional[str] = None,
        is_consumable: Optional[bool] = None,
        brand: Optional[str] = None,
        manufacturer_part_number: Optional[str] = None,
        product_id: Optional[str] = None,
        weight: Optional[Decimal] = None,
        length: Optional[Decimal] = None,
        width: Optional[Decimal] = None,
        height: Optional[Decimal] = None,
        renting_period: Optional[int] = None,
        quantity: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> InventoryItemMaster:
        return await self.update_use_case.execute(
            inventory_item_id=inventory_item_id,
            name=name,
            sku=sku,
            description=description,
            contents=contents,
            item_sub_category_id=item_sub_category_id,
            unit_of_measurement_id=unit_of_measurement_id,
            packaging_id=packaging_id,
            tracking_type=tracking_type,
            is_consumable=is_consumable,
            brand=brand,
            manufacturer_part_number=manufacturer_part_number,
            product_id=product_id,
            weight=weight,
            length=length,
            width=width,
            height=height,
            renting_period=renting_period,
            quantity=quantity,
            is_active=is_active
        )

    async def delete_inventory_item_master(self, inventory_item_id: UUID) -> bool:
        return await self.delete_use_case.execute(inventory_item_id)

    async def list_inventory_item_masters(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.list_use_case.execute(skip, limit)

    async def list_by_subcategory(self, subcategory_id: UUID, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.list_by_subcategory_use_case.execute(subcategory_id, skip, limit)

    async def list_by_tracking_type(self, tracking_type: str, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.list_by_tracking_type_use_case.execute(tracking_type, skip, limit)

    async def list_consumables(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.list_consumables_use_case.execute(skip, limit)

    async def search_inventory_item_masters(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[InventoryItemMaster]:
        return await self.search_use_case.execute(query, search_fields, limit)

    async def update_quantity(self, inventory_item_id: UUID, new_quantity: int) -> bool:
        return await self.update_quantity_use_case.execute(inventory_item_id, new_quantity)

    async def update_dimensions(
        self,
        inventory_item_id: UUID,
        weight: Optional[Decimal] = None,
        length: Optional[Decimal] = None,
        width: Optional[Decimal] = None,
        height: Optional[Decimal] = None
    ) -> InventoryItemMaster:
        return await self.update_dimensions_use_case.execute(
            inventory_item_id=inventory_item_id,
            weight=weight,
            length=length,
            width=width,
            height=height
        )

    async def count_inventory_item_masters(self) -> int:
        return await self.repository.count()

    async def count_by_subcategory(self, subcategory_id: UUID) -> int:
        return await self.repository.count_by_subcategory(subcategory_id)

    async def can_delete_inventory_item_master(self, inventory_item_id: UUID) -> bool:
        """Check if an inventory item master can be deleted (no associated line items)"""
        return await self.repository.can_delete(inventory_item_id)

    async def get_line_items_count(self, inventory_item_id: UUID) -> int:
        """Get the count of line items associated with an inventory item master"""
        return await self.repository.get_line_items_count(inventory_item_id)

    async def get_stats(self) -> dict:
        """Get statistics for inventory item masters"""
        return await self.repository.get_stats()