from typing import List, Optional

from ...domain.entities.warehouse import Warehouse
from ...domain.repositories.warehouse_repository import WarehouseRepository


class WarehouseService:
    def __init__(self, warehouse_repository: WarehouseRepository):
        self.warehouse_repository = warehouse_repository

    async def create_warehouse(
        self,
        name: str,
        label: str,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Warehouse:
        # Normalize label to uppercase for consistency
        normalized_label = label.upper() if label else ""
        
        # Check if label already exists
        existing_warehouse = await self.warehouse_repository.get_by_label(normalized_label)
        if existing_warehouse:
            raise ValueError(f"Warehouse with label '{normalized_label}' already exists")

        warehouse = Warehouse(
            name=name,
            label=label,
            remarks=remarks,
            created_by=created_by,
        )
        return await self.warehouse_repository.create(warehouse)

    async def get_warehouse_by_id(self, warehouse_id: str) -> Optional[Warehouse]:
        return await self.warehouse_repository.get_by_id(warehouse_id)

    async def get_warehouse_by_label(self, label: str) -> Optional[Warehouse]:
        return await self.warehouse_repository.get_by_label(label)

    async def get_all_warehouses(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Warehouse]:
        return await self.warehouse_repository.get_all(skip, limit, active_only)

    async def update_warehouse(
        self,
        warehouse_id: str,
        name: Optional[str] = None,
        label: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> Warehouse:
        warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse with id {warehouse_id} not found")

        # Check if new label conflicts with existing ones
        if label:
            normalized_label = label.upper()
            if normalized_label != warehouse.label:
                existing_warehouse = await self.warehouse_repository.get_by_label(normalized_label)
                if existing_warehouse:
                    raise ValueError(f"Warehouse with label '{normalized_label}' already exists")

        if name:
            warehouse.update_name(name)
        if label:
            warehouse.update_label(label)
        if remarks is not None:  # Allow clearing remarks
            warehouse.update_remarks(remarks)

        return await self.warehouse_repository.update(warehouse)

    async def deactivate_warehouse(self, warehouse_id: str) -> bool:
        warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse with id {warehouse_id} not found")

        warehouse.deactivate()
        await self.warehouse_repository.update(warehouse)
        return True

    async def activate_warehouse(self, warehouse_id: str) -> bool:
        warehouse = await self.warehouse_repository.get_by_id(warehouse_id)
        if not warehouse:
            raise ValueError(f"Warehouse with id {warehouse_id} not found")

        warehouse.activate()
        await self.warehouse_repository.update(warehouse)
        return True

    async def search_warehouses_by_name(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[Warehouse]:
        return await self.warehouse_repository.search_by_name(name, skip, limit)
