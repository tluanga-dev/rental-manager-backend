import re
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from .base_entity import BaseEntity


class IdManager(BaseEntity):
    """
    Manages unique ID generation with format: PREFIX-ABC0001
    Where:
    - ABC: Incrementing letters (AAA, AAB, ..., ZZZ, AAAA)
    - 0001: Incrementing numbers (0001-9999)
    """

    PREFIX_LENGTH = 3  # Standard length for prefix codes
    DEFAULT_LETTERS = "AAA"  # Starting letters for new sequences
    DEFAULT_NUMBERS = "0001"  # Starting numbers for new sequences

    def __init__(
        self,
        prefix: str,
        latest_id: Optional[str] = None,
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
        self._prefix = self._validate_prefix(prefix)
        self._latest_id = latest_id or f"{prefix}-{self.DEFAULT_LETTERS}{self.DEFAULT_NUMBERS}"

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def latest_id(self) -> str:
        return self._latest_id

    def update_latest_id(self, latest_id: str) -> None:
        """Update the latest ID for this prefix."""
        self._latest_id = latest_id
        self._touch_updated_at()

    def generate_next_id(self) -> str:
        """Generate the next ID in sequence for this prefix."""
        try:
            next_id = self._increment_id(self._latest_id, self._prefix)
        except ValueError:
            # Reset to default format if corrupted ID detected
            next_id = f"{self._prefix}-{self.DEFAULT_LETTERS}{self.DEFAULT_NUMBERS}"
        
        self._latest_id = next_id
        self._touch_updated_at()
        return next_id

    def _increment_id(self, last_id: str, expected_prefix: str) -> str:
        """
        Internal method to increment ID components with case insensitivity
        Validates format: [prefix]-[letters][numbers]
        """
        # Validate ID structure using regex
        if not re.match(rf"^{re.escape(expected_prefix)}-[A-Za-z]+\d+$", last_id):
            raise ValueError(f"Invalid ID format: {last_id}")

        # Split into prefix and sequence parts
        prefix_part, sequence_part = last_id.split("-", 1)
        match = re.match(r"^([A-Za-z]*)(\d+)$", sequence_part)

        if not match:
            raise ValueError(f"Invalid sequence format: {sequence_part}")

        # Extract and normalize letter case to uppercase
        letters = (match.group(1) or self.DEFAULT_LETTERS).upper()
        numbers = match.group(2)
        num_length = len(numbers)

        try:
            num = int(numbers)
        except ValueError:
            raise ValueError(f"Invalid numeric sequence: {numbers}")

        if num < (10**num_length - 1):
            # Increment number without changing letter sequence
            return f"{prefix_part}-{letters}{num + 1:0{num_length}d}"

        # Handle number overflow - increment letters and reset numbers
        new_letters = self._increment_letters(letters)
        return f"{prefix_part}-{new_letters}{self.DEFAULT_NUMBERS}"

    @staticmethod
    def _increment_letters(letters: str) -> str:
        """
        Increments letter sequence using right-to-left carryover
        Examples:
        'A' -> 'B'
        'Z' -> 'AA'
        'AZ' -> 'BA'
        'ZZZ' -> 'AAAA'
        """
        if not letters:  # Handle empty case
            return "A"

        chars = list(letters.upper())
        # Iterate from right to left
        for i in reversed(range(len(chars))):
            if chars[i] != "Z":
                chars[i] = chr(ord(chars[i]) + 1)  # Increment character
                return "".join(chars)
            chars[i] = "A"  # Reset to A and carry over

        # All characters were Z - add new character
        return "A" * (len(chars) + 1)

    def get_health_check_info(self) -> Dict[str, Any]:
        """
        Get health check information for this ID manager.
        """
        return {
            'prefix': self._prefix,
            'latest_id': self._latest_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def _validate_prefix(self, prefix: str) -> str:
        """Validate prefix format."""
        if not prefix or not prefix.strip():
            raise ValueError("Prefix cannot be empty")
        
        prefix = prefix.strip().upper()
        
        if len(prefix) > 255:
            raise ValueError("Prefix cannot exceed 255 characters")
        
        # Allow alphanumeric and underscore for prefix
        if not re.match(r'^[A-Z0-9_]+$', prefix):
            raise ValueError("Prefix can only contain uppercase letters, numbers, and underscores")
        
        return prefix

    def __str__(self) -> str:
        return f"{self._prefix}: {self._latest_id}"

    def __repr__(self) -> str:
        return f"IdManager(prefix='{self._prefix}', latest_id='{self._latest_id}')"
