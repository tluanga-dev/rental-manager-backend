"""Sales Transaction Item Entity

This module defines the SalesTransactionItem entity which represents individual
line items within a sales transaction.
"""

from decimal import Decimal
from typing import List, Optional

from src.domain.entities.base_entity import BaseEntity


class SalesTransactionItem(BaseEntity):
    """
    Represents an individual item within a sales transaction.
    
    This entity captures information about a specific product/item being sold
    including quantity, pricing, discounts, and taxes.
    """
    
    def __init__(
        self,
        transaction_id: str,
        inventory_item_master_id: str,
        warehouse_id: str,
        quantity: int,
        unit_price: Decimal,
        cost_price: Decimal = Decimal("0"),
        discount_percentage: Decimal = Decimal("0"),
        discount_amount: Decimal = Decimal("0"),
        tax_rate: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        subtotal: Decimal = Decimal("0"),
        total: Decimal = Decimal("0"),
        serial_numbers: Optional[List[str]] = None,
        notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a sales transaction item."""
        super().__init__(**kwargs)
        self.transaction_id = transaction_id
        self.inventory_item_master_id = inventory_item_master_id
        self.warehouse_id = warehouse_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.cost_price = cost_price
        self.discount_percentage = discount_percentage
        self.discount_amount = discount_amount
        self.tax_rate = tax_rate
        self.tax_amount = tax_amount
        self.subtotal = subtotal
        self.total = total
        self.serial_numbers = serial_numbers or []
        self.notes = notes
        
        # Calculate totals if not provided
        if self.total == Decimal("0"):
            self.calculate_totals()
    
    @property
    def profit_margin(self) -> Decimal:
        """
        Calculate the profit margin percentage for this item.
        
        Returns:
            The profit margin as a percentage
        """
        if self.cost_price > Decimal("0"):
            profit = self.unit_price - self.cost_price
            return (profit / self.cost_price) * Decimal("100")
        return Decimal("0")
    
    @property
    def total_profit(self) -> Decimal:
        """
        Calculate the total profit for this line item.
        
        Returns:
            The total profit amount
        """
        return (self.unit_price - self.cost_price) * Decimal(str(self.quantity))
    
    @property
    def effective_unit_price(self) -> Decimal:
        """
        Calculate the effective unit price after discounts.
        
        Returns:
            The unit price after applying discounts
        """
        if self.discount_percentage > Decimal("0"):
            discount_multiplier = Decimal("1") - (self.discount_percentage / Decimal("100"))
            return self.unit_price * discount_multiplier
        return self.unit_price
    
    def calculate_totals(self) -> None:
        """Calculate and update the subtotal and total for this item."""
        # Calculate base amount
        base_amount = self.unit_price * Decimal(str(self.quantity))
        
        # Apply discount
        if self.discount_percentage > Decimal("0"):
            self.discount_amount = base_amount * (self.discount_percentage / Decimal("100"))
        
        # Calculate subtotal (after discount)
        self.subtotal = base_amount - self.discount_amount
        
        # Calculate tax
        if self.tax_rate > Decimal("0"):
            self.tax_amount = self.subtotal * (self.tax_rate / Decimal("100"))
        else:
            self.tax_amount = Decimal("0")
        
        # Calculate total (including tax)
        self.total = self.subtotal + self.tax_amount
    
    def apply_bulk_discount(self) -> None:
        """Apply automatic bulk discount based on quantity."""
        # Only apply if no discount is already set
        if self.discount_percentage == Decimal("0"):
            if self.quantity >= 50:
                self.discount_percentage = Decimal("10")  # 10% for 50+ items
            elif self.quantity >= 10:
                self.discount_percentage = Decimal("5")   # 5% for 10+ items
            
            # Recalculate totals if discount was applied
            if self.discount_percentage > Decimal("0"):
                self.calculate_totals()
    
    def update_price(self, new_unit_price: Decimal) -> None:
        """
        Update the unit price and recalculate totals.
        
        Args:
            new_unit_price: The new unit price
            
        Raises:
            ValueError: If the price is negative
        """
        if new_unit_price < Decimal("0"):
            raise ValueError("Unit price cannot be negative")
        
        self.unit_price = new_unit_price
        self.calculate_totals()
    
    def validate_serial_numbers(self) -> None:
        """
        Validate that the number of serial numbers matches the quantity.
        
        Raises:
            ValueError: If serial numbers count doesn't match quantity
        """
        if self.serial_numbers and len(self.serial_numbers) != self.quantity:
            raise ValueError(
                f"Number of serial numbers ({len(self.serial_numbers)}) "
                f"must match quantity ({self.quantity})"
            )
    
    def can_be_returned(self, return_quantity: int) -> bool:
        """
        Check if the item can be returned.
        
        Args:
            return_quantity: The quantity to return
            
        Returns:
            True if the return is valid, False otherwise
        """
        return 0 < return_quantity <= self.quantity
    
    def __repr__(self) -> str:
        """Return string representation of the sales transaction item."""
        return (
            f"SalesTransactionItem(id={self.id}, transaction_id={self.transaction_id}, "
            f"inventory_item_master_id={self.inventory_item_master_id}, "
            f"quantity={self.quantity}, total={self.total})"
        )