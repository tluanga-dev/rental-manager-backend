from typing import Optional
from uuid import UUID
from datetime import datetime

from .base_entity import BaseEntity


class UnitOfMeasurement(BaseEntity):
    def __init__(
        self,
        name: str,
        abbreviation: str,
        description: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(
            entity_id=entity_id,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            is_active=is_active,
        )
        self._name = self._validate_name(name)
        self._abbreviation = self._validate_abbreviation(abbreviation)
        self._description = description.strip() if description else None

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
        self._name = self._validate_name(name)
        self._touch_updated_at()

    def update_abbreviation(self, abbreviation: str) -> None:
        self._abbreviation = self._validate_abbreviation(abbreviation)
        self._touch_updated_at()

    def update_description(self, description: Optional[str]) -> None:
        self._description = description.strip() if description else None
        self._touch_updated_at()

    def _validate_name(self, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if len(name.strip()) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return name.strip()

    def _validate_abbreviation(self, abbreviation: str) -> str:
        if not abbreviation or not abbreviation.strip():
            raise ValueError("Abbreviation cannot be empty")
        if len(abbreviation.strip()) > 8:
            raise ValueError("Abbreviation cannot exceed 8 characters")
        return abbreviation.strip()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"UnitOfMeasurement(id={self.id}, name='{self.name}', abbreviation='{self.abbreviation}')"
