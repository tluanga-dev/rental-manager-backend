"""Purchase Transaction Schemas

This module defines Pydantic schemas for purchase transaction API requests and responses.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from .base_schemas import CreateBaseSchema, UpdateBaseSchema, TimeStampedSchema


class PurchaseTransactionItemCreateSchema(BaseModel):
    """Schema for creating a purchase transaction item."""
    
    item_master_id: UUID = Field(..., description="Inventory item master ID")
    quantity: int = Field(..., gt=0, description="Quantity purchased")
    unit_price: Decimal = Field(..., ge=0, description="Unit purchase price")
    warehouse_id: Optional[UUID] = Field(None, description="Warehouse ID")
    serial_number: Optional[List[str]] = Field(
        default_factory=list,
        description="Serial numbers for individually tracked items"
    )
    discount: Optional[Decimal] = Field(
        default=Decimal("0"),
        ge=0,
        description="Discount amount"
    )
    tax_amount: Optional[Decimal] = Field(
        default=Decimal("0"),
        ge=0,
        description="Tax amount"
    )
    remarks: Optional[str] = Field(None, max_length=1000, description="Item remarks")
    warranty_period_type: Optional[str] = Field(
        None,
        description="Warranty period type (DAYS, MONTHS, YEARS)"
    )
    warranty_period: Optional[int] = Field(
        None,
        gt=0,
        description="Warranty period"
    )
    
    @field_validator('warranty_period_type')
    @classmethod
    def validate_warranty_period_type(cls, v):
        """Validate warranty period type."""
        if v is not None and v not in ["DAYS", "MONTHS", "YEARS"]:
            raise ValueError("Warranty period type must be DAYS, MONTHS, or YEARS")
        return v
    
    @field_validator('warranty_period')
    @classmethod
    def validate_warranty_period(cls, v, info):
        """Validate warranty period consistency."""
        warranty_type = info.data.get('warranty_period_type')
        
        # Both must be provided together or both must be None
        if (v is None) != (warranty_type is None):
            raise ValueError("Both warranty period type and warranty period must be provided together")
        
        return v


class PurchaseTransactionItemUpdateSchema(BaseModel):
    """Schema for updating a purchase transaction item."""
    
    unit_price: Optional[Decimal] = Field(None, ge=0, description="Unit purchase price")
    discount: Optional[Decimal] = Field(None, ge=0, description="Discount amount")
    tax_amount: Optional[Decimal] = Field(None, ge=0, description="Tax amount")
    remarks: Optional[str] = Field(None, max_length=1000, description="Item remarks")
    warranty_period_type: Optional[str] = Field(
        None,
        description="Warranty period type (DAYS, MONTHS, YEARS)"
    )
    warranty_period: Optional[int] = Field(
        None,
        gt=0,
        description="Warranty period"
    )
    
    @field_validator('warranty_period_type')
    @classmethod
    def validate_warranty_period_type(cls, v):
        """Validate warranty period type."""
        if v is not None and v not in ["DAYS", "MONTHS", "YEARS"]:
            raise ValueError("Warranty period type must be DAYS, MONTHS, or YEARS")
        return v


class PurchaseTransactionItemResponseSchema(TimeStampedSchema):
    """Schema for purchase transaction item response."""
    
    transaction_id: UUID
    inventory_item_id: UUID
    inventory_item: Optional[Dict[str, Any]] = Field(None, description="Inventory item details")
    warehouse_id: Optional[UUID]
    warehouse: Optional[Dict[str, Any]] = Field(None, description="Warehouse details")
    quantity: int
    unit_price: Decimal
    discount: Decimal
    tax_amount: Decimal
    total_price: Decimal
    serial_number: List[str]
    remarks: Optional[str]
    warranty_period_type: Optional[str]
    warranty_period: Optional[int]


class PurchaseTransactionCreateSchema(CreateBaseSchema):
    """Schema for creating a purchase transaction."""
    
    transaction_date: date = Field(..., description="Transaction date")
    vendor_id: UUID = Field(..., description="Vendor ID")
    transaction_id: Optional[str] = Field(None, max_length=255, description="Transaction ID (auto-generated if not provided)")
    purchase_order_number: Optional[str] = Field(None, max_length=255, description="Purchase order number")
    remarks: Optional[str] = Field(None, max_length=1000, description="Transaction remarks")
    
    @field_validator('transaction_date')
    @classmethod
    def validate_transaction_date(cls, v):
        """Validate transaction date is not in the future."""
        if v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v


class PurchaseTransactionCreateWithItemsSchema(CreateBaseSchema):
    """Schema for creating a purchase transaction with items."""
    
    transaction_date: date = Field(..., description="Transaction date")
    vendor_id: UUID = Field(..., description="Vendor ID")
    transaction_id: Optional[str] = Field(None, max_length=255, description="Transaction ID (auto-generated if not provided)")
    purchase_order_number: Optional[str] = Field(None, max_length=255, description="Purchase order number")
    remarks: Optional[str] = Field(None, max_length=1000, description="Transaction remarks")
    items: List[PurchaseTransactionItemCreateSchema] = Field(
        ...,
        min_length=1,
        description="Transaction items"
    )
    
    @field_validator('transaction_date')
    @classmethod
    def validate_transaction_date(cls, v):
        """Validate transaction date is not in the future."""
        if v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v


class PurchaseTransactionUpdateSchema(UpdateBaseSchema):
    """Schema for updating a purchase transaction."""
    
    transaction_date: Optional[date] = Field(None, description="Transaction date")
    vendor_id: Optional[UUID] = Field(None, description="Vendor ID")
    purchase_order_number: Optional[str] = Field(None, max_length=255, description="Purchase order number")
    remarks: Optional[str] = Field(None, max_length=1000, description="Transaction remarks")
    
    @field_validator('transaction_date')
    @classmethod
    def validate_transaction_date(cls, v):
        """Validate transaction date is not in the future."""
        if v is not None and v > date.today():
            raise ValueError("Transaction date cannot be in the future")
        return v


class PurchaseTransactionStatusUpdateSchema(BaseModel):
    """Schema for updating purchase transaction status."""
    
    status: str = Field(..., description="New transaction status")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status is a valid purchase status."""
        valid_statuses = ["DRAFT", "CONFIRMED", "PROCESSING", "RECEIVED", "COMPLETED", "CANCELLED"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of: {valid_statuses}")
        return v


class PurchaseTransactionResponseSchema(TimeStampedSchema):
    """Schema for purchase transaction response."""
    
    transaction_id: str
    transaction_date: date
    vendor_id: UUID
    vendor: Optional[Dict[str, Any]] = Field(None, description="Vendor details")
    status: str
    total_amount: Decimal
    grand_total: Decimal
    purchase_order_number: Optional[str]
    remarks: Optional[str]


class PurchaseTransactionWithItemsResponseSchema(PurchaseTransactionResponseSchema):
    """Schema for purchase transaction response with items."""
    
    items: List[PurchaseTransactionItemResponseSchema] = Field(
        default_factory=list,
        description="Transaction items"
    )
    item_summary: Optional[Dict[str, Any]] = Field(None, description="Item summary statistics")


class PurchaseTransactionListResponseSchema(BaseModel):
    """Schema for purchase transaction list response."""
    
    transactions: List[PurchaseTransactionResponseSchema]
    total: int = Field(..., description="Total number of transactions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class PurchaseTransactionFiltersSchema(BaseModel):
    """Schema for purchase transaction filters."""
    
    page: Optional[int] = Field(1, ge=1, description="Page number")
    page_size: Optional[int] = Field(50, ge=1, le=100, description="Page size")
    vendor_id: Optional[UUID] = Field(None, description="Filter by vendor ID")
    status: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[date] = Field(None, description="Filter by date from")
    date_to: Optional[date] = Field(None, description="Filter by date to")
    purchase_order_number: Optional[str] = Field(None, description="Filter by purchase order number")
    sort_by: Optional[str] = Field(None, description="Sort by field")
    sort_desc: Optional[bool] = Field(True, description="Sort in descending order")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status filter."""
        if v is not None:
            valid_statuses = ["DRAFT", "CONFIRMED", "PROCESSING", "RECEIVED", "COMPLETED", "CANCELLED"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
        return v


class PurchaseTransactionSearchSchema(BaseModel):
    """Schema for purchase transaction search."""
    
    query: str = Field(..., min_length=1, description="Search query")
    vendor_id: Optional[UUID] = Field(None, description="Filter by vendor ID")
    status: Optional[str] = Field(None, description="Filter by status")
    limit: Optional[int] = Field(100, ge=1, le=100, description="Maximum number of results")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        """Validate status filter."""
        if v is not None:
            valid_statuses = ["DRAFT", "CONFIRMED", "PROCESSING", "RECEIVED", "COMPLETED", "CANCELLED"]
            if v not in valid_statuses:
                raise ValueError(f"Status must be one of: {valid_statuses}")
        return v


class PurchaseTransactionStatisticsSchema(BaseModel):
    """Schema for purchase transaction statistics."""
    
    total_amount: Decimal = Field(..., description="Total purchase amount")
    total_transactions: int = Field(..., description="Total number of transactions")
    recent_amount: Decimal = Field(..., description="Recent period amount")
    recent_transactions: int = Field(..., description="Recent period transactions")
    status_counts: Dict[str, int] = Field(..., description="Count by status")


class PurchaseTransactionItemSummarySchema(BaseModel):
    """Schema for purchase transaction item summary."""
    
    total_items: int = Field(..., description="Total number of items")
    total_quantity: int = Field(..., description="Total quantity")
    total_amount: Decimal = Field(..., description="Total amount")
    total_discount: Decimal = Field(..., description="Total discount")
    total_tax: Decimal = Field(..., description="Total tax")
    average_unit_price: Decimal = Field(..., description="Average unit price")
    items_with_warranty: int = Field(..., description="Number of items with warranty")
    items_with_serial_numbers: int = Field(..., description="Number of items with serial numbers")


class BulkCreateItemsSchema(BaseModel):
    """Schema for bulk creating purchase transaction items."""
    
    items: List[PurchaseTransactionItemCreateSchema] = Field(
        ...,
        min_length=1,
        description="Items to create"
    )


class BulkCreateItemsResponseSchema(BaseModel):
    """Schema for bulk create items response."""
    
    created_items: List[PurchaseTransactionItemResponseSchema] = Field(
        ...,
        description="Created items"
    )
    total_created: int = Field(..., description="Total items created")
    total_requested: int = Field(..., description="Total items requested")
    transaction_id: UUID = Field(..., description="Transaction ID")
    updated_totals: Dict[str, Decimal] = Field(..., description="Updated transaction totals")