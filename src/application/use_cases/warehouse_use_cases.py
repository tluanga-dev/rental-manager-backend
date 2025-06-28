from typing import List, Optional
from uuid import UUID

from ...domain.entities.warehouse import Warehouse
from ..services.warehouse_service import WarehouseService


class WarehouseUseCases:
    def __init__(self, warehouse_service: WarehouseService):
        self.warehouse_service = warehouse_service

    async def create_warehouse(
        self,
        name: str,
        label: str,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Warehouse:
        """Create a new warehouse"""
        return await self.warehouse_service.create_warehouse(
            name=name,
            label=label,
            remarks=remarks,
            created_by=created_by,
        )

    async def get_warehouse(self, warehouse_id: UUID) -> Optional[Warehouse]:
        """Get warehouse by ID"""
        return await self.warehouse_service.get_warehouse_by_id(warehouse_id)

    async def get_warehouse_by_label(self, label: str) -> Optional[Warehouse]:
        """Get warehouse by label"""
        return await self.warehouse_service.get_warehouse_by_label(label)

    async def list_warehouses(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Warehouse]:
        """List all warehouses with pagination"""
        return await self.warehouse_service.get_all_warehouses(skip, limit, active_only)

    async def update_warehouse(
        self,
        warehouse_id: UUID,
        name: Optional[str] = None,
        label: Optional[str] = None,
        remarks: Optional[str] = None,
    ) -> Warehouse:
        """Update an existing warehouse"""
        return await self.warehouse_service.update_warehouse(
            warehouse_id=warehouse_id,
            name=name,
            label=label,
            remarks=remarks,
        )

    async def deactivate_warehouse(self, warehouse_id: UUID) -> bool:
        """Deactivate a warehouse (soft delete)"""
        return await self.warehouse_service.deactivate_warehouse(warehouse_id)

    async def activate_warehouse(self, warehouse_id: UUID) -> bool:
        """Activate a warehouse"""
        return await self.warehouse_service.activate_warehouse(warehouse_id)

    async def search_warehouses(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[Warehouse]:
        """Search warehouses by name"""
        return await self.warehouse_service.search_warehouses_by_name(name, skip, limit)
