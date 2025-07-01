from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field, validator
from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema


class InventoryItemMasterCreateSchema(CreateBaseSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Item name (must be unique)")
    sku: str = Field(..., min_length=1, max_length=255, description="Stock Keeping Unit (will be stored in uppercase)")
    description: Optional[str] = Field(None, description="Detailed description of the item")
    contents: Optional[str] = Field(None, description="Contents or composition of the item")
    item_sub_category_id: str = Field(..., description="Subcategory this item belongs to (UUID as string)")
    unit_of_measurement_id: str = Field(..., description="Unit of measurement for this item (UUID as string)")
    packaging_id: Optional[str] = Field(None, description="Packaging type for this item (UUID as string)")

    @validator('item_sub_category_id', 'unit_of_measurement_id')
    def validate_required_uuid_fields(cls, v):
        """Validate that UUID fields are valid UUID strings"""
        import uuid
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid UUID format')

    @validator('packaging_id')
    def validate_optional_uuid_field(cls, v):
        """Validate that optional UUID field is valid UUID string if provided"""
        if v is None:
            return v
        import uuid
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid UUID format')
    tracking_type: str = Field(..., description="Tracking type: BULK or INDIVIDUAL")
    is_consumable: bool = Field(False, description="Whether this item is consumable")
    brand: Optional[str] = Field(None, max_length=255, description="Product brand or manufacturer name")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255, description="Manufacturer's part number")
    product_id: Optional[str] = Field(None, max_length=255, description="Additional product identifier")
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight in kilograms")
    length: Optional[Decimal] = Field(None, ge=0, description="Length in centimeters")
    width: Optional[Decimal] = Field(None, ge=0, description="Width in centimeters")
    height: Optional[Decimal] = Field(None, ge=0, description="Height in centimeters")
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
    item_sub_category_id: Optional[str] = Field(None, description="Subcategory this item belongs to (UUID as string)")
    unit_of_measurement_id: Optional[str] = Field(None, description="Unit of measurement for this item (UUID as string)")
    packaging_id: Optional[str] = Field(None, description="Packaging type for this item (UUID as string)")

    @validator('item_sub_category_id', 'unit_of_measurement_id', 'packaging_id')
    def validate_uuid_fields(cls, v):
        """Validate that UUID fields are valid UUID strings if provided"""
        if v is None:
            return v
        import uuid
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid UUID format')
    tracking_type: Optional[str] = Field(None, description="Tracking type: BULK or INDIVIDUAL")
    is_consumable: Optional[bool] = Field(None, description="Whether this item is consumable")
    brand: Optional[str] = Field(None, max_length=255, description="Product brand or manufacturer name")
    manufacturer_part_number: Optional[str] = Field(None, max_length=255, description="Manufacturer's part number")
    product_id: Optional[str] = Field(None, max_length=255, description="Additional product identifier")
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight in kilograms")
    length: Optional[Decimal] = Field(None, ge=0, description="Length in centimeters")
    width: Optional[Decimal] = Field(None, ge=0, description="Width in centimeters")
    height: Optional[Decimal] = Field(None, ge=0, description="Height in centimeters")
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
    item_sub_category_id: str
    unit_of_measurement_id: str
    packaging_id: Optional[str] = None
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
    
    # Related entity names for frontend display
    item_category_name: Optional[str] = None
    item_sub_category_name: Optional[str] = None
    unit_of_measurement_name: Optional[str] = None
    packaging_name: Optional[str] = None
    
    # Delete functionality fields
    line_items_count: int = Field(default=0, description="Number of line items associated with this master item")
    can_delete: bool = Field(default=True, description="Whether this item can be deleted (no line items)")

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
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight in kilograms")
    length: Optional[Decimal] = Field(None, ge=0, description="Length in centimeters")
    width: Optional[Decimal] = Field(None, ge=0, description="Width in centimeters")
    height: Optional[Decimal] = Field(None, ge=0, description="Height in centimeters")


class InventoryItemMasterStatsSchema(BaseModel):
    total_masters: int = Field(description="Total number of item masters")
    bulk_items: int = Field(description="Number of bulk tracking items")
    individual_items: int = Field(description="Number of individual tracking items")
    consumable_items: int = Field(description="Number of consumable items")
    non_consumable_items: int = Field(description="Number of non-consumable items")
    total_inventory_instances: int = Field(description="Total inventory instances across all locations")