from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator
from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema


class InventoryItemMasterCreateSchema(CreateBaseSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Item name (must be unique)")
    sku: str = Field(..., min_length=1, max_length=255, description="Stock Keeping Unit (will be stored in uppercase)")
    description: Optional[str] = Field(None, description="Detailed description of the item")
    contents: Optional[str] = Field(None, description="Contents or composition of the item")
    item_sub_category_id: UUID = Field(..., description="Subcategory this item belongs to")
    unit_of_measurement_id: UUID = Field(..., description="Unit of measurement for this item")
    packaging_id: Optional[UUID] = Field(None, description="Packaging type for this item")
    tracking_type: str = Field(..., description="Tracking type: BULK or INDIVIDUAL")
    is_consumable: bool = Field(False, description="Whether this item is consumable")
    brand: Optional[str] = Field(None, max_length=255, description="Product brand or manufacturer name")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255, description="Manufacturer's part number")
    product_id: Optional[str] = Field(None, max_length=255, description="Additional product identifier")
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3, description="Weight in kilograms")
    length: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Length in centimeters")
    width: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Width in centimeters")
    height: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Height in centimeters")
    renting_period: int = Field(1, ge=1, description="Default rental period in days")
    quantity: int = Field(0, ge=0, description="Initial total stock quantity")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip()

    @validator('sku')
    def validate_sku(cls, v):
        if not v.strip():
            raise ValueError('SKU cannot be empty')
        return v.strip().upper()

    @validator('tracking_type')
    def validate_tracking_type(cls, v):
        if v not in ["BULK", "INDIVIDUAL"]:
            raise ValueError('Tracking type must be either BULK or INDIVIDUAL')
        return v

    @validator('weight', 'length', 'width', 'height')
    def validate_dimensions(cls, v):
        if v is not None and v < 0:
            raise ValueError('Dimensions cannot be negative')
        return v


class InventoryItemMasterUpdateSchema(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Item name (must be unique)")
    sku: Optional[str] = Field(None, min_length=1, max_length=255, description="Stock Keeping Unit (will be stored in uppercase)")
    description: Optional[str] = Field(None, description="Detailed description of the item")
    contents: Optional[str] = Field(None, description="Contents or composition of the item")
    item_sub_category_id: Optional[UUID] = Field(None, description="Subcategory this item belongs to")
    unit_of_measurement_id: Optional[UUID] = Field(None, description="Unit of measurement for this item")
    packaging_id: Optional[UUID] = Field(None, description="Packaging type for this item")
    tracking_type: Optional[str] = Field(None, description="Tracking type: BULK or INDIVIDUAL")
    is_consumable: Optional[bool] = Field(None, description="Whether this item is consumable")
    brand: Optional[str] = Field(None, max_length=255, description="Product brand or manufacturer name")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255, description="Manufacturer's part number")
    product_id: Optional[str] = Field(None, max_length=255, description="Additional product identifier")
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3, description="Weight in kilograms")
    length: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Length in centimeters")
    width: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Width in centimeters")
    height: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Height in centimeters")
    renting_period: Optional[int] = Field(None, ge=1, description="Default rental period in days")
    quantity: Optional[int] = Field(None, ge=0, description="Total stock quantity")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip() if v else v

    @validator('sku')
    def validate_sku(cls, v):
        if v is not None and not v.strip():
            raise ValueError('SKU cannot be empty')
        return v.strip().upper() if v else v

    @validator('tracking_type')
    def validate_tracking_type(cls, v):
        if v is not None and v not in ["BULK", "INDIVIDUAL"]:
            raise ValueError('Tracking type must be either BULK or INDIVIDUAL')
        return v


class InventoryItemMasterResponseSchema(TimeStampedSchema):
    name: str
    sku: str
    description: Optional[str] = None
    contents: Optional[str] = None
    item_sub_category_id: UUID
    unit_of_measurement_id: UUID
    packaging_id: Optional[UUID] = None
    tracking_type: str
    is_consumable: bool
    brand: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    product_id: Optional[str] = None
    weight: Optional[Decimal] = None
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    height: Optional[Decimal] = None
    renting_period: int
    quantity: int

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class InventoryItemMastersListResponseSchema(BaseModel):
    items: List[InventoryItemMasterResponseSchema]
    total: int
    skip: int
    limit: int


class InventoryItemMasterSearchSchema(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    search_fields: Optional[List[str]] = Field(
        None, 
        description="Fields to search in. Defaults to: name, sku, description, brand, manufacturer_part_number"
    )
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")

    @validator('search_fields')
    def validate_search_fields(cls, v):
        if v is None:
            return ["name", "sku", "description", "brand", "manufacturer_part_number"]
        
        allowed_fields = ["name", "sku", "description", "brand", "manufacturer_part_number", "product_id", "contents"]
        for field in v:
            if field not in allowed_fields:
                raise ValueError(f'Invalid search field: {field}. Allowed: {", ".join(allowed_fields)}')
        return v


class InventoryItemMasterQuantityUpdateSchema(BaseModel):
    quantity: int = Field(..., ge=0, description="New total quantity")


class InventoryItemMasterDimensionsUpdateSchema(BaseModel):
    weight: Optional[Decimal] = Field(None, ge=0, decimal_places=3, description="Weight in kilograms")
    length: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Length in centimeters")
    width: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Width in centimeters")
    height: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Height in centimeters")