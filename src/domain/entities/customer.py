import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from .base_entity import BaseEntity
from ..value_objects.address import Address


class Customer(BaseEntity):
    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        # Backward compatibility with Address value object
        address_vo: Optional[Address] = None,
        customer_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(
            entity_id=customer_id,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            is_active=is_active,
        )
        self._name = self._validate_name(name)
        self._email = self._validate_email(email) if email else None
        self._address = address.strip() if address else None
        self._remarks = remarks.strip() if remarks else None
        self._city = city.strip().title() if city else None
        
        # Backward compatibility
        self._address_vo = address_vo

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> Optional[str]:
        return self._email

    @property
    def address(self) -> Optional[str]:
        return self._address

    @property
    def remarks(self) -> Optional[str]:
        return self._remarks

    @property
    def city(self) -> Optional[str]:
        return self._city

    @property
    def address_vo(self) -> Optional[Address]:
        """Backward compatibility property"""
        return self._address_vo

    def update_name(self, name: str) -> None:
        self._name = self._validate_name(name)
        self._touch_updated_at()

    def update_email(self, email: Optional[str]) -> None:
        self._email = self._validate_email(email) if email else None
        self._touch_updated_at()

    def update_address(self, address: Optional[str]) -> None:
        self._address = address.strip() if address else None
        self._touch_updated_at()

    def update_remarks(self, remarks: Optional[str]) -> None:
        self._remarks = remarks.strip() if remarks else None
        self._touch_updated_at()

    def update_city(self, city: Optional[str]) -> None:
        self._city = city.strip().title() if city else None
        self._touch_updated_at()

    def update_address_vo(self, address_vo: Optional[Address]) -> None:
        """Backward compatibility method"""
        self._address_vo = address_vo
        self._touch_updated_at()

    @staticmethod
    def _validate_name(name: str) -> str:
        if not name or not name.strip():
            raise ValueError("Customer name cannot be empty")
        if len(name.strip()) < 2:
            raise ValueError("Customer name must be at least 2 characters long")
        return name.strip()

    @staticmethod
    def _validate_email(email: str) -> str:
        if not email:
            return email
        
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Invalid email format")
        return email

    def __str__(self) -> str:
        return f"Customer(id={self._id}, name={self._name}, email={self._email})"