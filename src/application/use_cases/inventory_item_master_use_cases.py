from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from ...domain.entities.inventory_item_master import InventoryItemMaster
from ...domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository


class CreateInventoryItemMasterUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(
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
        # Check if SKU already exists
        if await self.repository.exists_by_sku(sku):
            raise ValueError(f"An item with SKU '{sku}' already exists")
        
        # Check if name already exists
        if await self.repository.exists_by_name(name):
            raise ValueError(f"An item with name '{name}' already exists")
        
        inventory_item = InventoryItemMaster(
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
        
        return await self.repository.save(inventory_item)


class GetInventoryItemMasterUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, inventory_item_id: UUID) -> Optional[InventoryItemMaster]:
        return await self.repository.find_by_id(inventory_item_id)


class GetInventoryItemMasterBySkuUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, sku: str) -> Optional[InventoryItemMaster]:
        return await self.repository.find_by_sku(sku)


class UpdateInventoryItemMasterUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(
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
        inventory_item = await self.repository.find_by_id(inventory_item_id)
        if not inventory_item:
            raise ValueError(f"Inventory item with id {inventory_item_id} not found")
        
        # Check for duplicate SKU if changing it
        if sku and sku != inventory_item.sku:
            if await self.repository.exists_by_sku(sku, exclude_id=inventory_item_id):
                raise ValueError(f"An item with SKU '{sku}' already exists")
        
        # Check for duplicate name if changing it
        if name and name != inventory_item.name:
            if await self.repository.exists_by_name(name, exclude_id=inventory_item_id):
                raise ValueError(f"An item with name '{name}' already exists")
        
        # Update fields
        if name is not None:
            inventory_item.name = name
        if sku is not None:
            inventory_item.update_sku(sku)
        if description is not None:
            inventory_item.description = description
        if contents is not None:
            inventory_item.contents = contents
        if item_sub_category_id is not None:
            inventory_item.item_sub_category_id = item_sub_category_id
        if unit_of_measurement_id is not None:
            inventory_item.unit_of_measurement_id = unit_of_measurement_id
        if packaging_id is not None:
            inventory_item.packaging_id = packaging_id
        if tracking_type is not None:
            inventory_item.tracking_type = tracking_type
        if is_consumable is not None:
            if is_consumable:
                inventory_item.mark_as_consumable()
            else:
                inventory_item.is_consumable = False
        if brand is not None:
            inventory_item.brand = brand
        if manufacturer_part_number is not None:
            inventory_item.manufacturer_part_number = manufacturer_part_number
        if product_id is not None:
            inventory_item.product_id = product_id
        if weight is not None or length is not None or width is not None or height is not None:
            inventory_item.update_dimensions(weight, length, width, height)
        if renting_period is not None:
            inventory_item.renting_period = renting_period
        if quantity is not None:
            inventory_item.update_quantity(quantity)
        if is_active is not None:
            inventory_item.is_active = is_active
        
        return await self.repository.update(inventory_item)


class DeleteInventoryItemMasterUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, inventory_item_id: UUID) -> bool:
        return await self.repository.delete(inventory_item_id)


class ListInventoryItemMastersUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.repository.find_all(skip, limit)


class ListInventoryItemMastersBySubcategoryUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, subcategory_id: UUID, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.repository.find_by_subcategory(subcategory_id, skip, limit)


class ListInventoryItemMastersByTrackingTypeUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, tracking_type: str, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.repository.find_by_tracking_type(tracking_type, skip, limit)


class ListConsumableInventoryItemMastersUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[InventoryItemMaster]:
        return await self.repository.find_consumables(skip, limit)


class SearchInventoryItemMastersUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[InventoryItemMaster]:
        return await self.repository.search(query, search_fields, limit)


class UpdateInventoryItemMasterQuantityUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(self, inventory_item_id: UUID, new_quantity: int) -> bool:
        return await self.repository.update_quantity(inventory_item_id, new_quantity)


class UpdateInventoryItemMasterDimensionsUseCase:
    def __init__(self, repository: InventoryItemMasterRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        inventory_item_id: UUID,
        weight: Optional[Decimal] = None,
        length: Optional[Decimal] = None,
        width: Optional[Decimal] = None,
        height: Optional[Decimal] = None
    ) -> InventoryItemMaster:
        inventory_item = await self.repository.find_by_id(inventory_item_id)
        if not inventory_item:
            raise ValueError(f"Inventory item with id {inventory_item_id} not found")
        
        inventory_item.update_dimensions(weight, length, width, height)
        return await self.repository.update(inventory_item)