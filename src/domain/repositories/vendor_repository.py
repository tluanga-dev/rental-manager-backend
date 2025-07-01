from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.vendor import Vendor


class VendorRepository(ABC):
    @abstractmethod
    async def save(self, vendor: Vendor) -> Vendor:
        """Save a vendor entity to the database."""
        pass

    @abstractmethod
    async def find_by_id(self, vendor_id: str) -> Optional[Vendor]:
        """Find a vendor by its ID."""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> List[Vendor]:
        """Find vendors by name (case-insensitive partial match)."""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Vendor]:
        """Find a vendor by email address."""
        pass

    @abstractmethod
    async def find_by_city(self, city: str, limit: Optional[int] = None) -> List[Vendor]:
        """Find vendors by city (case-insensitive partial match)."""
        pass

    @abstractmethod
    async def search_vendors(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[Vendor]:
        """Search vendors across multiple fields."""
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Vendor]:
        """Find all vendors with pagination."""
        pass

    @abstractmethod
    async def update(self, vendor: Vendor) -> Vendor:
        """Update an existing vendor."""
        pass

    @abstractmethod
    async def delete(self, vendor_id: str) -> bool:
        """Delete a vendor by ID."""
        pass

    @abstractmethod
    async def exists(self, vendor_id: str) -> bool:
        """Check if a vendor exists by ID."""
        pass

    @abstractmethod
    async def exists_by_email(self, email: str, exclude_id: Optional[str] = None) -> bool:
        """Check if a vendor exists by email, optionally excluding a specific ID."""
        pass