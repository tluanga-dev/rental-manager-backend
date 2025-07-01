from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from .base_entity import BaseEntity


@dataclass
class LineItem(BaseEntity):
    inventory_item_master_id: str
    warehouse_id: str
    status: str = "AVAILABLE"
    serial_number: Optional[str] = None
    quantity: int = 1
    rental_rate: Decimal = Decimal("0.00")
    replacement_cost: Decimal = Decimal("0.00")
    late_fee_rate: Decimal = Decimal("0.00")
    sell_tax_rate: int = 0
    rent_tax_rate: int = 0
    rentable: bool = True
    sellable: bool = False
    selling_price: Decimal = Decimal("0.00")
    warranty_period_type: Optional[str] = None
    warranty_period: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if self.status not in ["AVAILABLE", "RENTED", "SOLD", "MAINTENANCE", "RETIRED", "LOST"]:
            raise ValueError(f"Invalid status: {self.status}")
        
        if self.serial_number:
            self.serial_number = self.serial_number.strip()
        
        if self.warranty_period_type and self.warranty_period_type not in ["DAYS", "MONTHS", "YEARS"]:
            raise ValueError(f"Invalid warranty period type: {self.warranty_period_type}")
        
        if self.warranty_period is not None and self.warranty_period < 0:
            raise ValueError("Warranty period cannot be negative")
        
        # Validate tax rates
        if self.sell_tax_rate < 0:
            raise ValueError("Sell tax rate cannot be negative")
            
        if self.rent_tax_rate < 0:
            raise ValueError("Rent tax rate cannot be negative")

    def update_status(self, new_status: str):
        """Update item status"""
        if new_status not in ["AVAILABLE", "RENTED", "SOLD", "MAINTENANCE", "RETIRED", "LOST"]:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        self.updated_at = datetime.now()

    def mark_as_rented(self):
        """Mark item as rented"""
        if self.status == "SOLD":
            raise ValueError("Cannot rent a sold item")
        if self.status == "RETIRED":
            raise ValueError("Cannot rent a retired item")
        if self.status == "LOST":
            raise ValueError("Cannot rent a lost item")
        self.status = "RENTED"
        self.updated_at = datetime.now()

    def mark_as_available(self):
        """Mark item as available"""
        if self.status == "SOLD":
            raise ValueError("Cannot make a sold item available")
        if self.status == "RETIRED":
            raise ValueError("Cannot make a retired item available")
        if self.status == "LOST":
            raise ValueError("Cannot make a lost item available")
        self.status = "AVAILABLE"
        self.updated_at = datetime.now()

    def sell(self):
        """Mark item as sold"""
        if not self.sellable:
            raise ValueError("This item is not sellable")
        if self.status != "AVAILABLE":
            raise ValueError("Only available items can be sold")
        self.status = "SOLD"
        self.updated_at = datetime.now()

    def retire(self):
        """Retire the item"""
        if self.status == "RENTED":
            raise ValueError("Cannot retire a rented item")
        self.status = "RETIRED"
        self.updated_at = datetime.now()

    def mark_as_lost(self):
        """Mark item as lost"""
        self.status = "LOST"
        self.updated_at = datetime.now()

    def update_pricing(self, rental_rate: Optional[Decimal] = None,
                      selling_price: Optional[Decimal] = None,
                      replacement_cost: Optional[Decimal] = None,
                      late_fee_rate: Optional[Decimal] = None):
        """Update pricing information"""
        if rental_rate is not None:
            if rental_rate < 0:
                raise ValueError("Rental rate cannot be negative")
            self.rental_rate = rental_rate
            
        if selling_price is not None:
            if selling_price < 0:
                raise ValueError("Selling price cannot be negative")
            self.selling_price = selling_price
            
        if replacement_cost is not None:
            if replacement_cost < 0:
                raise ValueError("Replacement cost cannot be negative")
            self.replacement_cost = replacement_cost
            
        if late_fee_rate is not None:
            if late_fee_rate < 0:
                raise ValueError("Late fee rate cannot be negative")
            self.late_fee_rate = late_fee_rate
            
        self.updated_at = datetime.now()

    def adjust_quantity(self, quantity_change: int):
        """Adjust quantity for bulk items"""
        new_quantity = self.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("Resulting quantity cannot be negative")
        self.quantity = new_quantity
        self.updated_at = datetime.now()

    def set_warranty(self, period_type: str, period: int):
        """Set warranty information"""
        if period_type not in ["DAYS", "MONTHS", "YEARS"]:
            raise ValueError(f"Invalid warranty period type: {period_type}")
        if period < 1:
            raise ValueError("Warranty period must be at least 1")
        self.warranty_period_type = period_type
        self.warranty_period = period
        self.updated_at = datetime.now()