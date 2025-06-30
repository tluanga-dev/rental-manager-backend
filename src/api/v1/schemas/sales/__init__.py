"""Sales API Schemas

This module contains all Pydantic schemas for sales-related API operations.
"""

from .sales_transaction_schemas import (
    SalesTransactionCreateSchema,
    SalesTransactionUpdateSchema,
    SalesTransactionResponseSchema,
    SalesTransactionDetailSchema,
    SalesTransactionItemCreateSchema,
    SalesTransactionItemResponseSchema,
    UpdatePaymentSchema,
    BulkPriceUpdateSchema,
    BulkPriceUpdateItemSchema,
    SalesTransactionListQuerySchema,
    SalesSummarySchema
)

from .sales_return_schemas import (
    SalesReturnCreateSchema,
    SalesReturnUpdateSchema,
    SalesReturnResponseSchema,
    SalesReturnDetailSchema,
    SalesReturnItemCreateSchema,
    SalesReturnItemResponseSchema,
    SalesReturnListQuerySchema,
    ApproveReturnSchema,
    ReturnSummarySchema
)

__all__ = [
    # Sales Transaction Schemas
    "SalesTransactionCreateSchema",
    "SalesTransactionUpdateSchema",
    "SalesTransactionResponseSchema",
    "SalesTransactionDetailSchema",
    "SalesTransactionItemCreateSchema",
    "SalesTransactionItemResponseSchema",
    "UpdatePaymentSchema",
    "BulkPriceUpdateSchema",
    "BulkPriceUpdateItemSchema",
    "SalesTransactionListQuerySchema",
    "SalesSummarySchema",
    
    # Sales Return Schemas
    "SalesReturnCreateSchema",
    "SalesReturnUpdateSchema",
    "SalesReturnResponseSchema",
    "SalesReturnDetailSchema",
    "SalesReturnItemCreateSchema",
    "SalesReturnItemResponseSchema",
    "SalesReturnListQuerySchema",
    "ApproveReturnSchema",
    "ReturnSummarySchema"
]