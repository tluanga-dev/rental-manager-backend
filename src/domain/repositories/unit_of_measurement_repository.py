from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.unit_of_measurement import UnitOfMeasurement


class UnitOfMeasurementRepository(ABC):
    @abstractmethod
    async def create(self, unit_of_measurement: UnitOfMeasurement) -> UnitOfMeasurement:
        """Create a new unit of measurement"""
        pass

    @abstractmethod
    async def get_by_id(self, unit_id: str) -> Optional[UnitOfMeasurement]:
        """Get unit of measurement by ID"""
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[UnitOfMeasurement]:
        """Get unit of measurement by name"""
        pass

    @abstractmethod
    async def get_by_abbreviation(self, abbreviation: str) -> Optional[UnitOfMeasurement]:
        """Get unit of measurement by abbreviation"""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[UnitOfMeasurement]:
        """Get all units of measurement with pagination"""
        pass

    @abstractmethod
    async def update(self, unit_of_measurement: UnitOfMeasurement) -> UnitOfMeasurement:
        """Update an existing unit of measurement"""
        pass

    @abstractmethod
    async def delete(self, unit_id: str) -> bool:
        """Delete a unit of measurement (soft delete)"""
        pass

    @abstractmethod
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[UnitOfMeasurement]:
        """Search units of measurement by name"""
        pass

    @abstractmethod
    async def count(self, active_only: bool = False) -> int:
        """Count units of measurement"""
        pass
