from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .base_schemas import CreateBaseSchema, UpdateBaseSchema, TimeStampedSchema


class PurchaseOrderStatus(str, Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    PARTIAL_RECEIVED = "PARTIAL_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class WarrantyPeriodType(str, Enum):
    DAYS = "DAYS"
    MONTHS = "MONTHS"
    YEARS = "YEARS"


class PurchaseOrderLineItemCreateSchema(BaseModel):
    inventory_item_master_id: UUID = Field(..., description="Inventory item master ID")
    warehouse_id: UUID = Field(..., description="Warehouse ID")
    quantity: int = Field(..., gt=0, description="Quantity to order")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    serial_number: Optional[str] = Field(None, max_length=255, description="Serial number for individual items")
    discount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Discount amount")
    tax_amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Tax amount")
    reference_number: Optional[str] = Field(None, max_length=255, description="Reference number")
    warranty_period_type: Optional[WarrantyPeriodType] = Field(None, description="Warranty period type")
    warranty_period: Optional[int] = Field(None, gt=0, description="Warranty period")
    rental_rate: Decimal = Field(default=Decimal("0.00"), ge=0, description="Rental rate")
    replacement_cost: Decimal = Field(default=Decimal("0.00"), ge=0, description="Replacement cost")
    late_fee_rate: Decimal = Field(default=Decimal("0.00"), ge=0, description="Late fee rate")
    sell_tax_rate: int = Field(default=0, ge=0, le=100, description="Sell tax rate percentage")
    rent_tax_rate: int = Field(default=0, ge=0, le=100, description="Rent tax rate percentage")
    rentable: bool = Field(default=True, description="Is item rentable")
    sellable: bool = Field(default=False, description="Is item sellable")
    selling_price: Decimal = Field(default=Decimal("0.00"), ge=0, description="Selling price")

    @field_validator("warranty_period")
    @classmethod
    def validate_warranty_period(cls, v: Optional[int], info) -> Optional[int]:
        if v is not None and info.data.get("warranty_period_type") is None:
            raise ValueError("warranty_period_type is required when warranty_period is specified")
        return v


class PurchaseOrderCreateSchema(CreateBaseSchema):
    vendor_id: UUID = Field(..., description="Vendor ID")
    order_date: date = Field(..., description="Order date")
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    reference_number: Optional[str] = Field(None, max_length=255, description="Reference number")
    invoice_number: Optional[str] = Field(None, max_length=255, description="Invoice number")
    notes: Optional[str] = Field(None, description="Additional notes")
    items: List[PurchaseOrderLineItemCreateSchema] = Field(..., min_length=1, description="Purchase order line items")

    @field_validator("expected_delivery_date")
    @classmethod
    def validate_delivery_date(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("order_date") and v < info.data["order_date"]:
            raise ValueError("Expected delivery date cannot be before order date")
        return v


class PurchaseOrderUpdateSchema(UpdateBaseSchema):
    vendor_id: Optional[UUID] = Field(None, description="Vendor ID")
    order_date: Optional[date] = Field(None, description="Order date")
    expected_delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    reference_number: Optional[str] = Field(None, max_length=255, description="Reference number")
    invoice_number: Optional[str] = Field(None, max_length=255, description="Invoice number")
    notes: Optional[str] = Field(None, description="Additional notes")


class PurchaseOrderReceiveItemSchema(BaseModel):
    line_item_id: UUID = Field(..., description="Line item ID")
    quantity: int = Field(..., gt=0, description="Quantity received")


class PurchaseOrderReceiveSchema(BaseModel):
    received_items: List[PurchaseOrderReceiveItemSchema] = Field(..., min_length=1, description="Items to receive")


class PurchaseOrderLineItemResponseSchema(TimeStampedSchema):
    id: UUID
    purchase_order_id: UUID
    inventory_item_master_id: UUID
    warehouse_id: UUID
    quantity: int
    unit_price: Decimal
    serial_number: Optional[str]
    discount: Decimal
    tax_amount: Decimal
    received_quantity: int
    reference_number: Optional[str]
    warranty_period_type: Optional[WarrantyPeriodType]
    warranty_period: Optional[int]
    rental_rate: Decimal
    replacement_cost: Decimal
    late_fee_rate: Decimal
    sell_tax_rate: int
    rent_tax_rate: int
    rentable: bool
    sellable: bool
    selling_price: Decimal
    amount: Decimal = Field(..., description="Line amount before tax")
    total_price: Decimal = Field(..., description="Total price including tax")
    is_fully_received: bool = Field(..., description="Whether all items have been received")
    remaining_quantity: int = Field(..., description="Quantity yet to be received")

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderResponseSchema(TimeStampedSchema):
    id: UUID
    order_number: str
    vendor_id: UUID
    order_date: date
    expected_delivery_date: Optional[date]
    status: PurchaseOrderStatus
    total_amount: Decimal
    total_tax_amount: Decimal
    total_discount: Decimal
    grand_total: Decimal
    reference_number: Optional[str]
    invoice_number: Optional[str]
    notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderDetailResponseSchema(PurchaseOrderResponseSchema):
    line_items: List[PurchaseOrderLineItemResponseSchema] = Field(default_factory=list)
    vendor_name: Optional[str] = Field(None, description="Vendor name")
    total_items: int = Field(..., description="Total number of line items")
    items_received: int = Field(..., description="Number of fully received items")
    items_pending: int = Field(..., description="Number of pending items")


class PurchaseOrderListQuerySchema(BaseModel):
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Number of records to return")
    vendor_id: Optional[UUID] = Field(None, description="Filter by vendor ID")
    status: Optional[PurchaseOrderStatus] = Field(None, description="Filter by status")
    start_date: Optional[date] = Field(None, description="Filter by start date")
    end_date: Optional[date] = Field(None, description="Filter by end date")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        if v and info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("End date cannot be before start date")
        return v


class PurchaseOrderSearchQuerySchema(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    search_fields: Optional[List[str]] = Field(
        default=["order_number", "reference_number", "invoice_number", "notes"],
        description="Fields to search in"
    )
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")


class PurchaseOrderSummaryResponseSchema(BaseModel):
    order_number: str
    vendor_id: UUID
    status: PurchaseOrderStatus
    order_date: date
    expected_delivery_date: Optional[date]
    grand_total: Decimal
    total_items: int
    items_received: int
    items_pending: int
    is_editable: bool
    is_receivable: bool

    model_config = ConfigDict(from_attributes=True)