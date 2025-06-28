from typing import Optional
from uuid import UUID
from datetime import datetime

from .base_entity import BaseEntity


class Vendor(BaseEntity):
    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        address: Optional[str] = None,
        remarks: Optional[str] = None,
        city: Optional[str] = None,
        vendor_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(vendor_id, created_at, updated_at, created_by, is_active)
        self._name = self._validate_name(name)
        self._email = self._validate_email(email) if email else None
        self._address = address
        self._remarks = remarks
        self._city = city

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

    def update_name(self, name: str) -> None:
        """Update vendor name with validation."""
        self._name = self._validate_name(name)
        self._update_timestamp()

    def update_email(self, email: Optional[str]) -> None:
        """Update vendor email with validation."""
        self._email = self._validate_email(email) if email else None
        self._update_timestamp()

    def update_address(self, address: Optional[str]) -> None:
        """Update vendor address."""
        self._address = address
        self._update_timestamp()

    def update_remarks(self, remarks: Optional[str]) -> None:
        """Update vendor remarks."""
        self._remarks = remarks
        self._update_timestamp()

    def update_city(self, city: Optional[str]) -> None:
        """Update vendor city."""
        self._city = city
        self._update_timestamp()

    def update_contact_info(
        self,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
    ) -> None:
        """Update multiple contact fields at once."""
        if email is not None:
            self._email = self._validate_email(email) if email else None
        if address is not None:
            self._address = address
        if city is not None:
            self._city = city
        self._update_timestamp()

    def get_display_info(self) -> dict:
        """Get vendor information for display purposes."""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "city": self.city,
            "is_active": self.is_active,
        }

    def matches_search_query(self, query: str, fields: list = None) -> bool:
        """Check if vendor matches a search query in specified fields."""
        if not query:
            return True
            
        if fields is None:
            fields = ["name", "email", "city", "remarks"]
        
        query_lower = query.lower()
        
        for field in fields:
            if field == "name" and self.name and query_lower in self.name.lower():
                return True
            elif field == "email" and self.email and query_lower in self.email.lower():
                return True
            elif field == "city" and self.city and query_lower in self.city.lower():
                return True
            elif field == "remarks" and self.remarks and query_lower in self.remarks.lower():
                return True
        
        return False

    @staticmethod
    def _validate_name(name: str) -> str:
        """Validate vendor name."""
        if not name or not name.strip():
            raise ValueError("Vendor name cannot be empty")
        
        name = name.strip()
        if len(name) > 255:
            raise ValueError("Vendor name cannot exceed 255 characters")
        
        return name

    @staticmethod
    def _validate_email(email: str) -> str:
        """Validate email format."""
        import re
        
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")
        
        email = email.strip().lower()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        if len(email) > 255:
            raise ValueError("Email cannot exceed 255 characters")
        
        return email

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Vendor(id={self.id}, name='{self.name}', email='{self.email}', is_active={self.is_active})"