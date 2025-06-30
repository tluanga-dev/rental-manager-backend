"""Purchase Status Value Object

This module defines the purchase status enumeration for purchase transactions.
"""

from enum import Enum


class PurchaseStatus(Enum):
    """
    Enumeration of possible purchase transaction statuses.
    """
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    
    def __str__(self) -> str:
        return self.value