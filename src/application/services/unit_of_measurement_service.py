from typing import List, Optional
from uuid import UUID

from ...domain.entities.unit_of_measurement import UnitOfMeasurement
from ...domain.repositories.unit_of_measurement_repository import UnitOfMeasurementRepository


class UnitOfMeasurementService:
    def __init__(self, unit_repository: UnitOfMeasurementRepository):
        self.unit_repository = unit_repository

    async def create_unit_of_measurement(
        self,
        name: str,
        abbreviation: str,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> UnitOfMeasurement:
        # Check if name already exists
        existing_unit_by_name = await self.unit_repository.get_by_name(name)
        if existing_unit_by_name:
            raise ValueError(f"Unit of measurement with name '{name}' already exists")

        # Check if abbreviation already exists
        existing_unit_by_abbr = await self.unit_repository.get_by_abbreviation(abbreviation)
        if existing_unit_by_abbr:
            raise ValueError(f"Unit of measurement with abbreviation '{abbreviation}' already exists")

        unit_of_measurement = UnitOfMeasurement(
            name=name,
            abbreviation=abbreviation,
            description=description,
            created_by=created_by,
        )
        return await self.unit_repository.create(unit_of_measurement)

    async def get_unit_by_id(self, unit_id: UUID) -> Optional[UnitOfMeasurement]:
        return await self.unit_repository.get_by_id(unit_id)

    async def get_unit_by_name(self, name: str) -> Optional[UnitOfMeasurement]:
        return await self.unit_repository.get_by_name(name)

    async def get_unit_by_abbreviation(self, abbreviation: str) -> Optional[UnitOfMeasurement]:
        return await self.unit_repository.get_by_abbreviation(abbreviation)

    async def get_all_units(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[UnitOfMeasurement]:
        return await self.unit_repository.get_all(skip, limit, active_only)

    async def update_unit_of_measurement(
        self,
        unit_id: UUID,
        name: Optional[str] = None,
        abbreviation: Optional[str] = None,
        description: Optional[str] = None,
    ) -> UnitOfMeasurement:
        unit = await self.unit_repository.get_by_id(unit_id)
        if not unit:
            raise ValueError(f"Unit of measurement with id {unit_id} not found")

        # Check for conflicts if name is being changed
        if name and name != unit.name:
            existing_unit = await self.unit_repository.get_by_name(name)
            if existing_unit:
                raise ValueError(f"Unit of measurement with name '{name}' already exists")

        # Check for conflicts if abbreviation is being changed
        if abbreviation and abbreviation != unit.abbreviation:
            existing_unit = await self.unit_repository.get_by_abbreviation(abbreviation)
            if existing_unit:
                raise ValueError(f"Unit of measurement with abbreviation '{abbreviation}' already exists")

        if name:
            unit.update_name(name)
        if abbreviation:
            unit.update_abbreviation(abbreviation)
        if description is not None:  # Allow clearing description
            unit.update_description(description)

        return await self.unit_repository.update(unit)

    async def deactivate_unit(self, unit_id: UUID) -> bool:
        unit = await self.unit_repository.get_by_id(unit_id)
        if not unit:
            raise ValueError(f"Unit of measurement with id {unit_id} not found")

        unit.deactivate()
        await self.unit_repository.update(unit)
        return True

    async def activate_unit(self, unit_id: UUID) -> bool:
        unit = await self.unit_repository.get_by_id(unit_id)
        if not unit:
            raise ValueError(f"Unit of measurement with id {unit_id} not found")

        unit.activate()
        await self.unit_repository.update(unit)
        return True

    async def search_units(self, name: str, skip: int = 0, limit: int = 100) -> List[UnitOfMeasurement]:
        return await self.unit_repository.search_by_name(name, skip, limit)

    async def count_units(self, active_only: bool = False) -> int:
        return await self.unit_repository.count(active_only)
