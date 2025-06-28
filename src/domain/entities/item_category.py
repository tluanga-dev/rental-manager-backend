from typing import Optional, List
from uuid import UUID
from datetime import datetime

from .base_entity import BaseEntity


class ItemCategory(BaseEntity):
    def __init__(
        self,
        name: str,
        abbreviation: str,
        description: Optional[str] = None,
        category_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(category_id, created_at, updated_at, created_by, is_active)
        self._name = self._validate_name(name)
        self._abbreviation = self._validate_and_clean_abbreviation(abbreviation)
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @property
    def description(self) -> Optional[str]:
        return self._description

    def update_name(self, name: str) -> None:
        """Update category name with validation."""
        self._name = self._validate_name(name)
        self._touch_updated_at()

    def update_abbreviation(self, abbreviation: str) -> None:
        """Update category abbreviation with validation."""
        self._abbreviation = self._validate_and_clean_abbreviation(abbreviation)
        self._touch_updated_at()

    def update_description(self, description: Optional[str]) -> None:
        """Update category description."""
        self._description = description
        self._touch_updated_at()

    def clean_fields(self) -> None:
        """Apply business rules - ensure abbreviation is uppercase."""
        if self._abbreviation:
            self._abbreviation = self._abbreviation.upper()

    def get_display_info(self) -> dict:
        """Get category information for display purposes."""
        return {
            "id": str(self.id),
            "name": self.name,
            "abbreviation": self.abbreviation,
            "description": self.description,
            "is_active": self.is_active,
        }

    @staticmethod
    def _validate_name(name: str) -> str:
        """Validate category name."""
        if not name or not name.strip():
            raise ValueError("Category name cannot be empty")
        
        name = name.strip()
        if len(name) > 255:
            raise ValueError("Category name cannot exceed 255 characters")
        
        return name

    @staticmethod
    def _validate_and_clean_abbreviation(abbreviation: str) -> str:
        """Validate and clean category abbreviation."""
        if not abbreviation or not abbreviation.strip():
            raise ValueError("Abbreviation cannot be empty")
        
        # Clean and uppercase
        abbreviation = abbreviation.strip().upper()
        
        if len(abbreviation) > 9:
            raise ValueError("Abbreviation cannot exceed 9 characters")
        
        return abbreviation

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"ItemCategory(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}', is_active={self.is_active})"


class ItemSubCategory(BaseEntity):
    def __init__(
        self,
        name: str,
        abbreviation: str,
        item_category_id: UUID,
        description: Optional[str] = None,
        subcategory_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(subcategory_id, created_at, updated_at, created_by, is_active)
        self._name = self._validate_name(name)
        self._abbreviation = self._validate_and_clean_abbreviation(abbreviation)
        self._item_category_id = item_category_id
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @property
    def item_category_id(self) -> UUID:
        return self._item_category_id

    @property
    def description(self) -> Optional[str]:
        return self._description

    def update_name(self, name: str) -> None:
        """Update subcategory name with validation."""
        self._name = self._validate_name(name)
        self._touch_updated_at()

    def update_abbreviation(self, abbreviation: str) -> None:
        """Update subcategory abbreviation with validation."""
        self._abbreviation = self._validate_and_clean_abbreviation(abbreviation)
        self._touch_updated_at()

    def update_description(self, description: Optional[str]) -> None:
        """Update subcategory description."""
        self._description = description
        self._touch_updated_at()

    def update_category(self, item_category_id: UUID) -> None:
        """Update parent category."""
        self._item_category_id = item_category_id
        self._touch_updated_at()

    def clean_fields(self) -> None:
        """Apply business rules - ensure abbreviation is uppercase."""
        if self._abbreviation:
            self._abbreviation = self._abbreviation.upper()

    def get_display_info(self) -> dict:
        """Get subcategory information for display purposes."""
        return {
            "id": str(self.id),
            "name": self.name,
            "abbreviation": self.abbreviation,
            "description": self.description,
            "item_category_id": str(self.item_category_id),
            "is_active": self.is_active,
        }

    @staticmethod
    def _validate_name(name: str) -> str:
        """Validate subcategory name."""
        if not name or not name.strip():
            raise ValueError("Subcategory name cannot be empty")
        
        name = name.strip()
        if len(name) > 255:
            raise ValueError("Subcategory name cannot exceed 255 characters")
        
        return name

    @staticmethod
    def _validate_and_clean_abbreviation(abbreviation: str) -> str:
        """Validate and clean subcategory abbreviation."""
        if not abbreviation or not abbreviation.strip():
            raise ValueError("Abbreviation cannot be empty")
        
        # Clean and uppercase
        abbreviation = abbreviation.strip().upper()
        
        if len(abbreviation) != 6:
            raise ValueError("Abbreviation must be exactly 6 characters")
        
        if not any(c.isalpha() for c in abbreviation):
            raise ValueError("Abbreviation must contain at least one letter")
        
        return abbreviation

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"ItemSubCategory(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}', category_id={self.item_category_id}, is_active={self.is_active})"