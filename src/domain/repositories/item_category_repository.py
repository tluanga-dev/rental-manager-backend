from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.item_category import ItemCategory, ItemSubCategory


class ItemCategoryRepository(ABC):
    @abstractmethod
    async def save(self, category: ItemCategory) -> ItemCategory:
        """Save a category entity to the database."""
        pass

    @abstractmethod
    async def find_by_id(self, category_id: UUID) -> Optional[ItemCategory]:
        """Find a category by its ID."""
        pass

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[ItemCategory]:
        """Find a category by name (exact match)."""
        pass

    @abstractmethod
    async def find_by_abbreviation(self, abbreviation: str) -> Optional[ItemCategory]:
        """Find a category by abbreviation (exact match)."""
        pass

    @abstractmethod
    async def search_categories(self, query: str, limit: int = 10) -> List[ItemCategory]:
        """Search categories by name or abbreviation."""
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ItemCategory]:
        """Find all categories with pagination."""
        pass

    @abstractmethod
    async def update(self, category: ItemCategory) -> ItemCategory:
        """Update an existing category."""
        pass

    @abstractmethod
    async def delete(self, category_id: UUID) -> bool:
        """Delete a category by ID."""
        pass

    @abstractmethod
    async def exists(self, category_id: UUID) -> bool:
        """Check if a category exists by ID."""
        pass

    @abstractmethod
    async def exists_by_name(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a category exists by name, optionally excluding a specific ID."""
        pass

    @abstractmethod
    async def exists_by_abbreviation(self, abbreviation: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a category exists by abbreviation, optionally excluding a specific ID."""
        pass


class ItemSubCategoryRepository(ABC):
    @abstractmethod
    async def save(self, subcategory: ItemSubCategory) -> ItemSubCategory:
        """Save a subcategory entity to the database."""
        pass

    @abstractmethod
    async def find_by_id(self, subcategory_id: UUID) -> Optional[ItemSubCategory]:
        """Find a subcategory by its ID."""
        pass

    @abstractmethod
    async def find_by_name_and_category(self, name: str, category_id: UUID) -> Optional[ItemSubCategory]:
        """Find a subcategory by name within a specific category."""
        pass

    @abstractmethod
    async def find_by_abbreviation(self, abbreviation: str) -> Optional[ItemSubCategory]:
        """Find a subcategory by abbreviation (exact match)."""
        pass

    @abstractmethod
    async def find_by_category(self, category_id: UUID, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        """Find all subcategories for a specific category."""
        pass

    @abstractmethod
    async def search_subcategories(self, query: str, category_id: Optional[UUID] = None, limit: int = 10) -> List[ItemSubCategory]:
        """Search subcategories by name or abbreviation, optionally within a category."""
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[ItemSubCategory]:
        """Find all subcategories with pagination."""
        pass

    @abstractmethod
    async def update(self, subcategory: ItemSubCategory) -> ItemSubCategory:
        """Update an existing subcategory."""
        pass

    @abstractmethod
    async def delete(self, subcategory_id: UUID) -> bool:
        """Delete a subcategory by ID."""
        pass

    @abstractmethod
    async def exists(self, subcategory_id: UUID) -> bool:
        """Check if a subcategory exists by ID."""
        pass

    @abstractmethod
    async def exists_by_name_and_category(self, name: str, category_id: UUID, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a subcategory exists by name within a category, optionally excluding a specific ID."""
        pass

    @abstractmethod
    async def exists_by_abbreviation(self, abbreviation: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a subcategory exists by abbreviation, optionally excluding a specific ID."""
        pass