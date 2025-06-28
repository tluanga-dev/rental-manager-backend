from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from .base_entity import BaseEntity


class InventoryItemMaster(BaseEntity):
    def __init__(
        self,
        name: str,
        sku: str,
        item_sub_category_id: UUID,
        unit_of_measurement_id: UUID,
        tracking_type: str,
        is_consumable: bool = False,
        description: Optional[str] = None,
        contents: Optional[str] = None,
        packaging_id: Optional[UUID] = None,
        brand: Optional[str] = None,
        manufacturer_part_number: Optional[str] = None,
        product_id: Optional[str] = None,
        weight: Optional[Decimal] = None,
        length: Optional[Decimal] = None,
        width: Optional[Decimal] = None,
        height: Optional[Decimal] = None,
        renting_period: int = 1,
        quantity: int = 0,
        inventory_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(
            entity_id=inventory_id,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            is_active=is_active,
        )
        
        self._name = name.strip() if name else ""
        self._sku = sku.strip().upper() if sku else ""
        self._item_sub_category_id = item_sub_category_id
        self._unit_of_measurement_id = unit_of_measurement_id
        self._tracking_type = tracking_type
        self._is_consumable = is_consumable
        self._description = description
        self._contents = contents
        self._packaging_id = packaging_id
        self._brand = brand
        self._manufacturer_part_number = manufacturer_part_number
        self._product_id = product_id
        self._weight = weight
        self._length = length
        self._width = width
        self._height = height
        self._renting_period = renting_period
        self._quantity = quantity
        
        self._validate()

    def _validate(self):
        if not self._name:
            raise ValueError("Item name is required")
        
        if not self._sku:
            raise ValueError("SKU is required")
        
        if self._tracking_type not in ["BULK", "INDIVIDUAL"]:
            raise ValueError("Tracking type must be either BULK or INDIVIDUAL")
        
        if self._renting_period < 1:
            raise ValueError("Renting period must be at least 1 day")
        
        if self._quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        # Validate dimensions if provided
        if self._weight is not None and self._weight < 0:
            raise ValueError("Weight cannot be negative")
        
        if self._length is not None and self._length < 0:
            raise ValueError("Length cannot be negative")
            
        if self._width is not None and self._width < 0:
            raise ValueError("Width cannot be negative")
            
        if self._height is not None and self._height < 0:
            raise ValueError("Height cannot be negative")

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        if not value or not value.strip():
            raise ValueError("Item name is required")
        self._name = value.strip()
        self._touch_updated_at()

    @property
    def sku(self) -> str:
        return self._sku

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]):
        self._description = value
        self._touch_updated_at()

    @property
    def contents(self) -> Optional[str]:
        return self._contents

    @contents.setter
    def contents(self, value: Optional[str]):
        self._contents = value
        self._touch_updated_at()

    @property
    def item_sub_category_id(self) -> UUID:
        return self._item_sub_category_id

    @item_sub_category_id.setter
    def item_sub_category_id(self, value: UUID):
        self._item_sub_category_id = value
        self._touch_updated_at()

    @property
    def unit_of_measurement_id(self) -> UUID:
        return self._unit_of_measurement_id

    @unit_of_measurement_id.setter
    def unit_of_measurement_id(self, value: UUID):
        self._unit_of_measurement_id = value
        self._touch_updated_at()

    @property
    def packaging_id(self) -> Optional[UUID]:
        return self._packaging_id

    @packaging_id.setter
    def packaging_id(self, value: Optional[UUID]):
        self._packaging_id = value
        self._touch_updated_at()

    @property
    def tracking_type(self) -> str:
        return self._tracking_type

    @tracking_type.setter
    def tracking_type(self, value: str):
        if value not in ["BULK", "INDIVIDUAL"]:
            raise ValueError("Tracking type must be either BULK or INDIVIDUAL")
        self._tracking_type = value
        self._touch_updated_at()

    @property
    def is_consumable(self) -> bool:
        return self._is_consumable

    @is_consumable.setter
    def is_consumable(self, value: bool):
        self._is_consumable = value
        self._touch_updated_at()

    @property
    def brand(self) -> Optional[str]:
        return self._brand

    @brand.setter
    def brand(self, value: Optional[str]):
        self._brand = value
        self._touch_updated_at()

    @property
    def manufacturer_part_number(self) -> Optional[str]:
        return self._manufacturer_part_number

    @manufacturer_part_number.setter
    def manufacturer_part_number(self, value: Optional[str]):
        self._manufacturer_part_number = value
        self._touch_updated_at()

    @property
    def product_id(self) -> Optional[str]:
        return self._product_id

    @product_id.setter
    def product_id(self, value: Optional[str]):
        self._product_id = value
        self._touch_updated_at()

    @property
    def weight(self) -> Optional[Decimal]:
        return self._weight

    @property
    def length(self) -> Optional[Decimal]:
        return self._length

    @property
    def width(self) -> Optional[Decimal]:
        return self._width

    @property
    def height(self) -> Optional[Decimal]:
        return self._height

    @property
    def renting_period(self) -> int:
        return self._renting_period

    @renting_period.setter
    def renting_period(self, value: int):
        if value < 1:
            raise ValueError("Renting period must be at least 1 day")
        self._renting_period = value
        self._touch_updated_at()

    @property
    def quantity(self) -> int:
        return self._quantity

    def update_quantity(self, new_quantity: int):
        """Update the total quantity across all warehouses"""
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self._quantity = new_quantity
        self._touch_updated_at()

    def mark_as_consumable(self):
        """Mark item as consumable"""
        self._is_consumable = True
        self._touch_updated_at()

    def update_dimensions(self, weight: Optional[Decimal] = None, 
                         length: Optional[Decimal] = None,
                         width: Optional[Decimal] = None, 
                         height: Optional[Decimal] = None):
        """Update physical dimensions"""
        if weight is not None:
            if weight < 0:
                raise ValueError("Weight cannot be negative")
            self._weight = weight
        
        if length is not None:
            if length < 0:
                raise ValueError("Length cannot be negative")
            self._length = length
            
        if width is not None:
            if width < 0:
                raise ValueError("Width cannot be negative")
            self._width = width
            
        if height is not None:
            if height < 0:
                raise ValueError("Height cannot be negative")
            self._height = height
            
        self._touch_updated_at()

    def update_sku(self, new_sku: str):
        """Update SKU (normalized to uppercase)"""
        if not new_sku or not new_sku.strip():
            raise ValueError("SKU cannot be empty")
        self._sku = new_sku.strip().upper()
        self._touch_updated_at()