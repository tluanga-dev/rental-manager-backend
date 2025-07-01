from typing import List, Optional


from ...domain.entities.unit_of_measurement import UnitOfMeasurement
from ..services.unit_of_measurement_service import UnitOfMeasurementService


class UnitOfMeasurementUseCases:
    def __init__(self, unit_service: UnitOfMeasurementService):
        self.unit_service = unit_service

    async def create_unit_of_measurement(
        self,
        name: str,
        abbreviation: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> UnitOfMeasurement:
        """Create a new unit of measurement"""
        return await self.unit_service.create_unit_of_measurement(
            name=name,
            abbreviation=abbreviation,
            description=description,
            created_by=created_by,
        )

    async def get_unit_of_measurement(self, unit_id: str) -> Optional[UnitOfMeasurement]:
        """Get unit of measurement by ID"""
        return await self.unit_service.get_unit_by_id(unit_id)

    async def get_unit_by_name(self, name: str) -> Optional[UnitOfMeasurement]:
        """Get unit of measurement by name"""
        return await self.unit_service.get_unit_by_name(name)

    async def get_unit_by_abbreviation(self, abbreviation: str) -> Optional[UnitOfMeasurement]:
        """Get unit of measurement by abbreviation"""
        return await self.unit_service.get_unit_by_abbreviation(abbreviation)

    async def list_units_of_measurement(
        self, skip: int = 0, limit: int = 100, is_active: bool = True
    ) -> List[UnitOfMeasurement]:
        """List all units of measurement with pagination"""
        return await self.unit_service.get_all_units(skip, limit, is_active)

    async def update_unit_of_measurement(
        self,
        unit_id: str,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UnitOfMeasurement:
        """Update an existing unit of measurement"""
        return await self.unit_service.update_unit_of_measurement(
            unit_id=unit_id,
            name=name,
            abbreviation=abbreviation,
            description=description,
        )

    async def deactivate_unit_of_measurement(self, unit_id: str) -> bool:
        """Deactivate a unit of measurement (soft delete)"""
        return await self.unit_service.deactivate_unit(unit_id)

    async def activate_unit_of_measurement(self, unit_id: str) -> bool:
        """Activate a unit of measurement"""
        return await self.unit_service.activate_unit(unit_id)

    async def search_units_of_measurement(
        self, name: str, skip: int = 0, limit: int = 100
    ) -> List[UnitOfMeasurement]:
        """Search units of measurement by name or abbreviation"""
        return await self.unit_service.search_units(name, skip, limit)

    async def count_units_of_measurement(self, is_active: Optional[bool] = None) -> int:
        """Count units of measurement"""
        # If is_active is True or False, use active_only accordingly
        # If is_active is None, count all units (active_only=False)
        active_only = is_active if is_active is not None else False
        return await self.unit_service.count_units(active_only)
