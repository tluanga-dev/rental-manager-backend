"""Purchase Transaction Item Entity

This module defines the PurchaseTransactionItem entity which represents individual
items within a purchase transaction. It handles inventory creation and serial number
management according to the PRD requirements.
"""

from decimal import Decimal
from typing import List, Optional

from src.domain.entities.base_entity import BaseEntity


class PurchaseTransactionItem(BaseEntity):
    """
    Represents an individual item within a purchase transaction.
    
    This entity handles the business logic for inventory item creation,
    serial number management, and cost distribution as specified in the PRD.
    """
    
    def __init__(
        self,
        transaction_id: str,
        inventory_item_id: str,
        quantity: int,
        unit_price: Decimal,
        warehouse_id: Optional[str] = None,
        serial_number: Optional[List[str]] = None,
        discount: Decimal = Decimal("0.00"),
        tax_amount: Decimal = Decimal("0.00"),
        total_price: Optional[Decimal] = None,
        remarks: Optional[str] = None,
        warranty_period_type: Optional[str] = None,
        warranty_period: Optional[int] = None,
        **kwargs
    ):
        """Initialize a purchase transaction item."""
        super().__init__(**kwargs)
        self.transaction_id = transaction_id
        self.inventory_item_id = inventory_item_id
        self.quantity = self._validate_quantity(quantity)
        self.unit_price = self._validate_amount(unit_price)
        self.warehouse_id = warehouse_id
        self.serial_number = serial_number or []
        self.discount = self._validate_amount(discount)
        self.tax_amount = self._validate_amount(tax_amount)
        self.total_price = total_price or self._calculate_total_price()
        self.remarks = remarks
        self.warranty_period_type = self._validate_warranty_period_type(warranty_period_type)
        self.warranty_period = warranty_period
        
        # Validate warranty period consistency
        self._validate_warranty_period_consistency()
    
    @staticmethod
    def _validate_quantity(quantity: int) -> int:
        """Validate that quantity is positive."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        return quantity
    
    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        """Validate that amount is non-negative."""
        if amount < Decimal("0"):
            raise ValueError("Amount cannot be negative")
        return amount
    
    @staticmethod
    def _validate_warranty_period_type(warranty_type: Optional[str]) -> Optional[str]:
        """Validate warranty period type."""
        if warranty_type is None:
            return None
        
        valid_types = ["DAYS", "MONTHS", "YEARS"]
        if warranty_type not in valid_types:
            raise ValueError(f"Warranty period type must be one of: {valid_types}")
        
        return warranty_type
    
    def _validate_warranty_period_consistency(self) -> None:
        """Validate that warranty period and type are consistent."""
        has_type = self.warranty_period_type is not None
        has_period = self.warranty_period is not None
        
        if has_type != has_period:
            raise ValueError(
                "Both warranty period type and warranty period must be provided together"
            )
        
        if self.warranty_period is not None and self.warranty_period <= 0:
            raise ValueError("Warranty period must be greater than 0")
    
    def _calculate_total_price(self) -> Decimal:
        """Calculate the total price for this item."""
        subtotal = self.unit_price * self.quantity
        total = subtotal - self.discount + self.tax_amount
        return max(total, Decimal("0"))  # Ensure non-negative
    
    def validate_serial_numbers_for_tracking_type(self, tracking_type: str) -> None:
        """
        Validate serial numbers based on tracking type as per PRD requirements.
        
        Args:
            tracking_type: Either "INDIVIDUAL" or "BULK"
            
        Raises:
            ValueError: If serial numbers don't match tracking requirements
        """
        if tracking_type == "INDIVIDUAL":
            if not self.serial_number:
                raise ValueError(
                    f"Individual tracking items require {self.quantity} serial number"
                    f"{'s' if self.quantity > 1 else ''}"
                )
            
            if len(self.serial_number) != self.quantity:
                raise ValueError(
                    f"Number of serial numbers ({len(self.serial_number)}) "
                    f"must match quantity ({self.quantity})"
                )
            
            # Check for duplicates within this item
            unique_serials = set(self.serial_number)
            if len(unique_serials) != len(self.serial_number):
                raise ValueError("Serial numbers must be unique")
        
        elif tracking_type == "BULK":
            # For bulk items, serial numbers are optional
            if self.serial_number and len(self.serial_number) > 0:
                # If provided, there should be at most one serial number for bulk items
                if len(self.serial_number) > 1:
                    raise ValueError("Bulk tracked items can have at most one serial number")
    
    def update_pricing(
        self, 
        unit_price: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None
    ) -> None:
        """
        Update pricing information and recalculate totals.
        
        Args:
            unit_price: New unit price
            discount: New discount amount
            tax_amount: New tax amount
        """
        if unit_price is not None:
            self.unit_price = self._validate_amount(unit_price)
        
        if discount is not None:
            self.discount = self._validate_amount(discount)
        
        if tax_amount is not None:
            self.tax_amount = self._validate_amount(tax_amount)
        
        # Recalculate total price
        self.total_price = self._calculate_total_price()
    
    def update_warranty(
        self, 
        warranty_period_type: Optional[str] = None,
        warranty_period: Optional[int] = None
    ) -> None:
        """
        Update warranty information.
        
        Args:
            warranty_period_type: New warranty period type
            warranty_period: New warranty period
        """
        self.warranty_period_type = self._validate_warranty_period_type(warranty_period_type)
        self.warranty_period = warranty_period
        self._validate_warranty_period_consistency()
    
    def add_serial_number(self, serial_number: str) -> None:
        """
        Add a serial number to this item.
        
        Args:
            serial_number: The serial number to add
            
        Raises:
            ValueError: If serial number already exists in this item
        """
        if serial_number in self.serial_number:
            raise ValueError(f"Serial number '{serial_number}' already exists for this item")
        
        self.serial_number.append(serial_number)
    
    def remove_serial_number(self, serial_number: str) -> None:
        """
        Remove a serial number from this item.
        
        Args:
            serial_number: The serial number to remove
            
        Raises:
            ValueError: If serial number doesn't exist
        """
        if serial_number not in self.serial_number:
            raise ValueError(f"Serial number '{serial_number}' not found")
        
        self.serial_number.remove(serial_number)
    
    @property
    def has_warranty(self) -> bool:
        """Check if this item has warranty information."""
        return self.warranty_period_type is not None and self.warranty_period is not None
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate subtotal (unit price * quantity)."""
        return self.unit_price * self.quantity
    
    @property
    def discount_percentage(self) -> Decimal:
        """Calculate discount as percentage of subtotal."""
        if self.subtotal == 0:
            return Decimal("0")
        return (self.discount / self.subtotal) * 100
    
    def __repr__(self) -> str:
        """Return string representation of the purchase transaction item."""
        return (
            f"PurchaseTransactionItem(id={self.id}, transaction_id={self.transaction_id}, "
            f"inventory_item_id={self.inventory_item_id}, quantity={self.quantity}, "
            f"total_price={self.total_price})"
        )