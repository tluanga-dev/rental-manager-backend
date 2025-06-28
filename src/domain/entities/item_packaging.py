from typing import Optional
from uuid import UUID
from datetime import datetime

from .base_entity import BaseEntity


class ItemPackaging(BaseEntity):
    def __init__(
        self,
        name: str,
        label: str,
        unit: str,
        remarks: Optional[str] = None,
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
        self._label = self._normalize_label(label)
        self._unit = self._validate_unit(unit)
        self._remarks = remarks.strip() if remarks else None

    @property
    def name(self) -> str:
        return self._name

    @property
    def label(self) -> str:
        return self._label

    @property
    def unit(self) -> str:
        return self._unit

    @property
    def remarks(self) -> Optional[str]:
        return self._remarks

    def update_name(self, name: str) -> None:
        self._name = self._validate_name(name)
        self._touch_updated_at()

    def update_label(self, label: str) -> None:
        self._label = self._normalize_label(label)
        self._touch_updated_at()

    def update_unit(self, unit: str) -> None:
        self._unit = self._validate_unit(unit)
        self._touch_updated_at()

    def update_remarks(self, remarks: Optional[str]) -> None:
        self._remarks = remarks.strip() if remarks else None
        self._touch_updated_at()

    def _validate_name(self, name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        if len(name.strip()) > 255:
            raise ValueError("Name cannot exceed 255 characters")
        return name.strip()

    def _normalize_label(self, label: str) -> str:
        if not label or not label.strip():
            raise ValueError("Label cannot be empty")
        normalized_label = label.strip().upper()
        if len(normalized_label) > 255:
            raise ValueError("Label cannot exceed 255 characters")
        return normalized_label

    def _validate_unit(self, unit: str) -> str:
        if not unit or not unit.strip():
            raise ValueError("Unit cannot be empty")
        if len(unit.strip()) > 255:
            raise ValueError("Unit cannot exceed 255 characters")
        return unit.strip()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"ItemPackaging(id={self.id}, name='{self.name}', label='{self.label}', unit='{self.unit}')"
