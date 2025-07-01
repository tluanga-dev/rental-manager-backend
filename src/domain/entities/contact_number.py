from datetime import datetime
from typing import Optional

from .base_entity import BaseEntity
from ..value_objects.phone_number import PhoneNumber


class ContactNumber(BaseEntity):
    def __init__(
        self,
        phone_number: PhoneNumber,
        entity_type: str,
        entity_id: str,
        contact_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(
            entity_id=contact_id,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            is_active=is_active,
        )
        self._phone_number = phone_number
        self._entity_type = self._validate_entity_type(entity_type)
        self._entity_id = entity_id

    @property
    def phone_number(self) -> PhoneNumber:
        return self._phone_number

    @property
    def entity_type(self) -> str:
        return self._entity_type

    @property
    def entity_id(self) -> str:
        return self._entity_id

    def update_phone_number(self, phone_number: PhoneNumber) -> None:
        self._phone_number = phone_number
        self._touch_updated_at()

    def update_entity_reference(self, entity_type: str, entity_id: str) -> None:
        self._entity_type = self._validate_entity_type(entity_type)
        self._entity_id = entity_id
        self._touch_updated_at()

    @staticmethod
    def _validate_entity_type(entity_type: str) -> str:
        if not entity_type or not entity_type.strip():
            raise ValueError("Entity type cannot be empty")
        
        # Validate entity type format (should be a valid model name)
        allowed_entity_types = ["Customer", "User", "Supplier", "Property", "Unit"]
        if entity_type not in allowed_entity_types:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        return entity_type.strip()

    def __str__(self) -> str:
        return f"ContactNumber({self._phone_number.number} -> {self._entity_type}:{self._entity_id})"