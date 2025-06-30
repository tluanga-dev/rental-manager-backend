"""Sales Return Schemas

This module defines Pydantic schemas for sales return API requests and responses.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator

from ..base_schemas import TimeStampedSchema
from .sales_transaction_schemas import SalesTransactionResponseSchema, SalesTransactionItemResponseSchema


class SalesReturnItemCreateSchema(BaseModel):
    """Schema for creating a sales return item."""
    
    sales_item_id: UUID = Field(..., description="Original sales transaction item ID")
    quantity: int = Field(..., gt=0, description="Quantity to return")
    condition: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Condition of returned item (e.g., new, unopened, damaged)"
    )
    serial_numbers: Optional[List[str]] = Field(
        default_factory=list,
        description="Serial numbers of returned items"
    )
    
    @validator('condition')
    def validate_condition(cls, v):
        """Validate condition is not empty."""
        if not v.strip():
            raise ValueError('Condition cannot be empty')
        return v.strip()
    
    @validator('serial_numbers')
    def validate_serial_numbers(cls, v, values):
        """Validate serial numbers match quantity."""
        if v and 'quantity' in values:
            if len(v) != values['quantity']:
                raise ValueError(
                    f"Number of serial numbers ({len(v)}) must match quantity ({values['quantity']})"
                )
        return v


class SalesReturnItemResponseSchema(TimeStampedSchema):
    """Schema for sales return item response."""
    
    id: UUID
    sales_return_id: UUID
    sales_item_id: UUID
    sales_item: Optional[SalesTransactionItemResponseSchema] = None
    quantity: int
    condition: str
    serial_numbers: List[str]
    is_resellable: bool = Field(False, description="Whether item can be resold")


class SalesReturnCreateSchema(BaseModel):
    """Schema for creating a sales return."""
    
    sales_transaction_id: UUID = Field(..., description="Original sales transaction ID")
    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Reason for return"
    )
    items: List[SalesReturnItemCreateSchema] = Field(
        ...,
        min_items=1,
        description="Items being returned"
    )
    restocking_fee: Optional[Decimal] = Field(
        default=Decimal("0"),
        ge=0,
        decimal_places=2,
        description="Restocking fee to charge"
    )
    
    @validator('reason')
    def validate_reason(cls, v):
        """Validate reason is not empty."""
        if not v.strip():
            raise ValueError('Return reason cannot be empty')
        if len(v.strip()) < 10:
            raise ValueError('Return reason must be at least 10 characters')
        return v.strip()


class SalesReturnUpdateSchema(BaseModel):
    """Schema for updating a sales return."""
    
    reason: Optional[str] = Field(None, min_length=10, max_length=500)
    restocking_fee: Optional[Decimal] = Field(None, ge=0, decimal_places=2)


class SalesReturnResponseSchema(TimeStampedSchema):
    """Schema for sales return response."""
    
    id: UUID
    return_id: str
    sales_transaction_id: UUID
    sales_transaction: Optional[SalesTransactionResponseSchema] = None
    return_date: datetime
    reason: str
    approved_by_id: Optional[UUID]
    approved_by_name: Optional[str] = Field(None, description="Name of approver")
    refund_amount: Decimal
    restocking_fee: Decimal
    net_refund_amount: Decimal = Field(..., description="Refund amount after restocking fee")
    is_approved: bool


class SalesReturnDetailSchema(SalesReturnResponseSchema):
    """Schema for detailed sales return response with items."""
    
    items: List[SalesReturnItemResponseSchema] = Field(
        default_factory=list,
        description="Return line items"
    )


class SalesReturnListQuerySchema(BaseModel):
    """Schema for sales return list query parameters."""
    
    sales_transaction_id: Optional[UUID] = Field(None, description="Filter by transaction")
    approved_by_id: Optional[UUID] = Field(None, description="Filter by approver")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    is_approved: Optional[bool] = Field(None, description="Filter by approval status")
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum records to return")
    sort_by: Optional[str] = Field(
        default="return_date",
        description="Field to sort by"
    )
    sort_desc: bool = Field(default=True, description="Sort in descending order")


class ApproveReturnSchema(BaseModel):
    """Schema for approving a return."""
    
    notes: Optional[str] = Field(None, max_length=500, description="Approval notes")


class ReturnSummarySchema(BaseModel):
    """Schema for return summary statistics."""
    
    total_returns: int
    total_refunded: Decimal
    total_restocking_fees: Decimal
    net_refunded: Decimal
    average_refund: Decimal
    approved_returns: int
    pending_returns: int
    top_return_reasons: List[dict]