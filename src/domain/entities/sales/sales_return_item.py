"""Sales Return Item Entity

This module defines the SalesReturnItem entity which represents individual
items being returned within a sales return.
"""

from typing import List, Optional

from src.domain.entities.base_entity import BaseEntity


class SalesReturnItem(BaseEntity):
    """
    Represents an individual item within a sales return.
    
    This entity captures information about specific items being returned
    including quantity, condition, and serial numbers.
    """
    
    def __init__(
        self,
        sales_return_id: str,
        sales_item_id: str,
        quantity: int,
        condition: str,
        serial_numbers: Optional[List[str]] = None,
        **kwargs
    ):
        """Initialize a sales return item."""
        super().__init__(**kwargs)
        self.sales_return_id = sales_return_id
        self.sales_item_id = sales_item_id
        self.quantity = quantity
        self.condition = condition
        self.serial_numbers = serial_numbers or []
    
    def validate_quantity(self, original_quantity: int) -> None:
        """
        Validate that the return quantity is valid.
        
        Args:
            original_quantity: The original quantity sold
            
        Raises:
            ValueError: If the return quantity is invalid
        """
        if self.quantity <= 0:
            raise ValueError("Return quantity must be greater than zero")
        
        if self.quantity > original_quantity:
            raise ValueError(
                f"Return quantity ({self.quantity}) cannot exceed "
                f"original quantity ({original_quantity})"
            )
    
    def validate_serial_numbers(self) -> None:
        """
        Validate that serial numbers match the quantity.
        
        Raises:
            ValueError: If serial numbers don't match quantity
        """
        if self.serial_numbers and len(self.serial_numbers) != self.quantity:
            raise ValueError(
                f"Number of serial numbers ({len(self.serial_numbers)}) "
                f"must match return quantity ({self.quantity})"
            )
    
    def validate_condition(self) -> None:
        """
        Validate that a condition is specified.
        
        Raises:
            ValueError: If condition is not specified
        """
        if not self.condition or not self.condition.strip():
            raise ValueError("Item condition must be specified")
    
    def is_resellable(self) -> bool:
        """
        Check if the item can be resold based on condition.
        
        Returns:
            True if the item can be resold
        """
        # Define conditions that allow resale
        resellable_conditions = [
            "new", "unopened", "like new", "excellent", "good"
        ]
        
        return self.condition.lower() in resellable_conditions
    
    def __repr__(self) -> str:
        """Return string representation of the sales return item."""
        return (
            f"SalesReturnItem(id={self.id}, sales_return_id={self.sales_return_id}, "
            f"sales_item_id={self.sales_item_id}, quantity={self.quantity}, "
            f"condition={self.condition})"
        )