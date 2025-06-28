from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID, uuid4

from .base_entity import BaseEntity


@dataclass
class InventoryItemMaster(BaseEntity):
    name: str
    sku: str
    item_sub_category_id: UUID
    unit_of_measurement_id: UUID
    tracking_type: str
    is_consumable: bool = False
    description: Optional[str] = None
    contents: Optional[str] = None
    packaging_id: Optional[UUID] = None
    brand: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    product_id: Optional[str] = None
    weight: Optional[Decimal] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    renting_period: int = 1
    quantity: int = 0

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        if not self.name or not self.name.strip():
            raise ValueError("Item name is required")
        
        if not self.sku or not self.sku.strip():
            raise ValueError("SKU is required")
        
        # Normalize SKU to uppercase
        self.sku = self.sku.strip().upper()
        
        if self.tracking_type not in ["BULK", "INDIVIDUAL"]:
            raise ValueError("Tracking type must be either BULK or INDIVIDUAL")
        
        if self.renting_period < 1:
            raise ValueError("Renting period must be at least 1 day")
        
        if self.quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        # Validate dimensions if provided
        if self.weight is not None and self.weight < 0:
            raise ValueError("Weight cannot be negative")
        
        if self.length is not None and self.length < 0:
            raise ValueError("Length cannot be negative")
            
        if self.width is not None and self.width < 0:
            raise ValueError("Width cannot be negative")
            
        if self.height is not None and self.height < 0:
            raise ValueError("Height cannot be negative")

    def update_quantity(self, new_quantity: int):
        """Update the total quantity across all warehouses"""
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity = new_quantity
        self.updated_at = datetime.now()

    def mark_as_consumable(self):
        """Mark item as consumable"""
        self.is_consumable = True
        self.updated_at = datetime.now()

    def update_dimensions(self, weight: Optional[Decimal] = None, 
                         length: Optional[Decimal] = None,
                         width: Optional[Decimal] = None, 
                         height: Optional[Decimal] = None):
        """Update physical dimensions"""
        if weight is not None:
            if weight < 0:
                raise ValueError("Weight cannot be negative")
            self.weight = weight
        
        if length is not None:
            if length < 0:
                raise ValueError("Length cannot be negative")
            self.length = length
            
        if width is not None:
            if width < 0:
                raise ValueError("Width cannot be negative")
            self.width = width
            
        if height is not None:
            if height < 0:
                raise ValueError("Height cannot be negative")
            self.height = height
            
        self.updated_at = datetime.now()

    def update_sku(self, new_sku: str):
        """Update SKU (normalized to uppercase)"""
        if not new_sku or not new_sku.strip():
            raise ValueError("SKU cannot be empty")
        self.sku = new_sku.strip().upper()
        self.updated_at = datetime.now()