"""Sales Transaction Schemas

This module defines Pydantic schemas for sales transaction API requests and responses.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ..base_schemas import TimeStampedSchema
from ..customer_schemas import CustomerResponseSchema


class SalesTransactionItemCreateSchema(BaseModel):
    """Schema for creating a sales transaction item."""
    
    inventory_item_master_id: UUID = Field(..., description="Inventory item master ID")
    warehouse_id: UUID = Field(..., description="Warehouse ID")
    quantity: int = Field(..., gt=0, description="Quantity to sell")
    unit_price: Decimal = Field(..., ge=0, decimal_places=2, description="Unit selling price")
    discount_percentage: Optional[Decimal] = Field(
        default=Decimal("0"),
        ge=0,
        le=100,
        decimal_places=2,
        description="Discount percentage"
    )
    tax_rate: Optional[Decimal] = Field(
        default=Decimal("0"),
        ge=0,
        le=100,
        decimal_places=2,
        description="Tax rate percentage"
    )
    serial_numbers: Optional[List[str]] = Field(
        default_factory=list,
        description="Serial numbers for individually tracked items"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Item notes")
    
    @validator('serial_numbers')
    def validate_serial_numbers(cls, v, values):
        """Validate serial numbers match quantity for individually tracked items."""
        if v and 'quantity' in values:
            if len(v) != values['quantity']:
                raise ValueError(
                    f"Number of serial numbers ({len(v)}) must match quantity ({values['quantity']})"
                )
        return v


class SalesTransactionItemResponseSchema(TimeStampedSchema):
    """Schema for sales transaction item response."""
    
    id: UUID
    transaction_id: UUID
    inventory_item_master_id: UUID
    inventory_item_master_name: Optional[str] = Field(None, description="Item name")
    inventory_item_master_sku: Optional[str] = Field(None, description="Item SKU")
    warehouse_id: UUID
    warehouse_name: Optional[str] = Field(None, description="Warehouse name")
    quantity: int
    unit_price: Decimal
    cost_price: Decimal
    discount_percentage: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    subtotal: Decimal
    total: Decimal
    profit_margin: Optional[Decimal] = Field(None, description="Profit margin percentage")
    serial_numbers: List[str]
    notes: Optional[str]


class SalesTransactionCreateSchema(BaseModel):
    """Schema for creating a sales transaction."""
    
    customer_id: UUID = Field(..., description="Customer ID")
    items: List[SalesTransactionItemCreateSchema] = Field(
        ...,
        min_items=1,
        description="List of items to sell"
    )
    order_date: Optional[datetime] = Field(None, description="Order date (defaults to now)")
    delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    payment_terms: str = Field(
        default="IMMEDIATE",
        regex="^(IMMEDIATE|NET_15|NET_30|NET_45|NET_60|NET_90|COD|PREPAID)$",
        description="Payment terms"
    )
    shipping_amount: Optional[Decimal] = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=2,
        description="Shipping charges"
    )
    shipping_address: Optional[str] = Field(None, max_length=500, description="Shipping address")
    billing_address: Optional[str] = Field(None, max_length=500, description="Billing address")
    purchase_order_number: Optional[str] = Field(
        None,
        max_length=50,
        description="Customer's purchase order number"
    )
    sales_person_id: Optional[UUID] = Field(None, description="Sales person ID")
    notes: Optional[str] = Field(None, description="Internal notes")
    customer_notes: Optional[str] = Field(None, description="Customer notes")


class SalesTransactionUpdateSchema(BaseModel):
    """Schema for updating a sales transaction."""
    
    delivery_date: Optional[datetime] = Field(None, description="Expected delivery date")
    shipping_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    shipping_address: Optional[str] = Field(None, max_length=500)
    billing_address: Optional[str] = Field(None, max_length=500)
    purchase_order_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None)
    customer_notes: Optional[str] = Field(None)


class SalesTransactionResponseSchema(TimeStampedSchema):
    """Schema for sales transaction response."""
    
    id: UUID
    transaction_id: str
    invoice_number: Optional[str]
    customer_id: UUID
    customer: Optional[CustomerResponseSchema] = None
    order_date: datetime
    delivery_date: Optional[datetime]
    status: str
    payment_status: str
    payment_terms: str
    payment_due_date: Optional[date]
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    grand_total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    is_overdue: bool
    days_overdue: int
    shipping_address: Optional[str]
    billing_address: Optional[str]
    purchase_order_number: Optional[str]
    sales_person_id: Optional[UUID]
    notes: Optional[str]
    customer_notes: Optional[str]


class SalesTransactionDetailSchema(SalesTransactionResponseSchema):
    """Schema for detailed sales transaction response with items."""
    
    items: List[SalesTransactionItemResponseSchema] = Field(
        default_factory=list,
        description="Transaction line items"
    )


class UpdatePaymentSchema(BaseModel):
    """Schema for updating payment information."""
    
    amount_paid: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Total amount paid (not incremental)"
    )
    payment_notes: Optional[str] = Field(
        None,
        max_length=500,
        description="Payment notes"
    )


class BulkPriceUpdateItemSchema(BaseModel):
    """Schema for bulk price update item."""
    
    id: UUID = Field(..., description="Sales transaction item ID")
    unit_price: Decimal = Field(..., ge=0, decimal_places=2, description="New unit price")


class BulkPriceUpdateSchema(BaseModel):
    """Schema for bulk price update."""
    
    items: List[BulkPriceUpdateItemSchema] = Field(
        ...,
        min_items=1,
        description="Items to update"
    )


class SalesTransactionListQuerySchema(BaseModel):
    """Schema for sales transaction list query parameters."""
    
    customer_id: Optional[UUID] = Field(None, description="Filter by customer")
    status: Optional[str] = Field(
        None,
        regex="^(DRAFT|CONFIRMED|PROCESSING|SHIPPED|DELIVERED|CANCELLED)$",
        description="Filter by status"
    )
    payment_status: Optional[str] = Field(
        None,
        regex="^(PENDING|PARTIAL|PAID|OVERDUE|REFUNDED)$",
        description="Filter by payment status"
    )
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    is_overdue: Optional[bool] = Field(None, description="Filter overdue transactions")
    search: Optional[str] = Field(None, description="Search in transaction/invoice/PO number")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return")
    sort_by: Optional[str] = Field(
        default="order_date",
        description="Field to sort by"
    )
    sort_desc: bool = Field(default=True, description="Sort in descending order")


class SalesSummarySchema(BaseModel):
    """Schema for sales summary statistics."""
    
    total_sales: Decimal
    total_orders: int
    total_paid: Decimal
    total_outstanding: Decimal
    average_order_value: Decimal
    daily_breakdown: Optional[List[dict]] = None
    top_selling_items: Optional[List[dict]] = None