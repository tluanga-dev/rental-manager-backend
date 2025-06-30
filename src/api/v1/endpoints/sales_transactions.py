"""Sales Transactions API Endpoints

This module defines the FastAPI endpoints for sales transaction operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.config.database import get_db_session
from ....application.use_cases.sales import (
    CreateSalesTransactionUseCase,
    ConfirmSalesOrderUseCase,
    UpdatePaymentUseCase
)
from ....infrastructure.repositories.sales_transaction_repository_impl import SQLAlchemySalesTransactionRepository
from ....infrastructure.repositories.sales_transaction_item_repository_impl import SQLAlchemySalesTransactionItemRepository
from ....infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from ....infrastructure.repositories.inventory_item_master_repository_impl import SQLAlchemyInventoryItemMasterRepository
from ....infrastructure.repositories.warehouse_repository_impl import SQLAlchemyWarehouseRepository
from ....infrastructure.repositories.id_manager_repository_impl import SQLAlchemyIdManagerRepository
from ....infrastructure.repositories.inventory_stock_movement_service import InventoryStockMovementService
from ..schemas.sales import (
    SalesTransactionCreateSchema,
    SalesTransactionUpdateSchema,
    SalesTransactionResponseSchema,
    SalesTransactionDetailSchema,
    UpdatePaymentSchema,
    BulkPriceUpdateSchema,
    SalesTransactionListQuerySchema,
    SalesSummarySchema
)

router = APIRouter(prefix="/sales/transactions", tags=["sales-transactions"])


def get_repositories(db: Session = Depends(get_db_session)) -> Dict[str, Any]:
    """Get all required repositories."""
    return {
        'sales_repository': SQLAlchemySalesTransactionRepository(db),
        'sales_item_repository': SQLAlchemySalesTransactionItemRepository(db),
        'customer_repository': SQLAlchemyCustomerRepository(db),
        'inventory_repository': SQLAlchemyInventoryItemMasterRepository(db),
        'warehouse_repository': SQLAlchemyWarehouseRepository(db),
        'id_manager_repository': SQLAlchemyIdManagerRepository(db),
        'stock_movement_service': InventoryStockMovementService(db)
    }


async def transaction_to_response_schema(
    transaction,
    repositories: Dict[str, Any],
    include_items: bool = False
) -> SalesTransactionResponseSchema:
    """Convert transaction entity to response schema."""
    # Get customer details
    customer = await repositories['customer_repository'].find_by_id(transaction.customer_id)
    
    response_data = {
        'id': transaction.id,
        'transaction_id': transaction.transaction_id,
        'invoice_number': transaction.invoice_number,
        'customer_id': transaction.customer_id,
        'customer': {
            'id': customer.id,
            'name': customer.name,
            'email': customer.email
        } if customer else None,
        'order_date': transaction.order_date,
        'delivery_date': transaction.delivery_date,
        'status': transaction.status.value,
        'payment_status': transaction.payment_status.value,
        'payment_terms': transaction.payment_terms.value,
        'payment_due_date': transaction.payment_due_date,
        'subtotal': transaction.subtotal,
        'discount_amount': transaction.discount_amount,
        'tax_amount': transaction.tax_amount,
        'shipping_amount': transaction.shipping_amount,
        'grand_total': transaction.grand_total,
        'amount_paid': transaction.amount_paid,
        'balance_due': transaction.balance_due,
        'is_overdue': transaction.is_overdue,
        'days_overdue': transaction.days_overdue,
        'shipping_address': transaction.shipping_address,
        'billing_address': transaction.billing_address,
        'purchase_order_number': transaction.purchase_order_number,
        'sales_person_id': transaction.sales_person_id,
        'notes': transaction.notes,
        'customer_notes': transaction.customer_notes,
        'created_at': transaction.created_at,
        'updated_at': transaction.updated_at,
        'created_by': transaction.created_by,
        'is_active': transaction.is_active
    }
    
    if include_items:
        # Get transaction items
        items = await repositories['sales_item_repository'].get_by_transaction(transaction.id)
        items_data = []
        
        for item in items:
            # Get inventory and warehouse details
            inventory = await repositories['inventory_repository'].find_by_id(item.inventory_item_master_id)
            warehouse = await repositories['warehouse_repository'].find_by_id(item.warehouse_id)
            
            items_data.append({
                'id': item.id,
                'transaction_id': item.transaction_id,
                'inventory_item_master_id': item.inventory_item_master_id,
                'inventory_item_master_name': inventory.name if inventory else None,
                'inventory_item_master_sku': inventory.sku if inventory else None,
                'warehouse_id': item.warehouse_id,
                'warehouse_name': warehouse.name if warehouse else None,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'cost_price': item.cost_price,
                'discount_percentage': item.discount_percentage,
                'discount_amount': item.discount_amount,
                'tax_rate': item.tax_rate,
                'tax_amount': item.tax_amount,
                'subtotal': item.subtotal,
                'total': item.total,
                'profit_margin': item.profit_margin,
                'serial_numbers': item.serial_numbers,
                'notes': item.notes,
                'created_at': item.created_at,
                'updated_at': item.updated_at,
                'created_by': item.created_by,
                'is_active': item.is_active
            })
        
        return SalesTransactionDetailSchema(**response_data, items=items_data)
    
    return SalesTransactionResponseSchema(**response_data)


@router.post("/", response_model=SalesTransactionDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_sales_transaction(
    transaction_data: SalesTransactionCreateSchema,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Create a new sales transaction."""
    try:
        use_case = CreateSalesTransactionUseCase(**repositories)
        
        transaction, items = await use_case.execute(
            customer_id=transaction_data.customer_id,
            items=[item.dict() for item in transaction_data.items],
            order_date=transaction_data.order_date,
            delivery_date=transaction_data.delivery_date,
            payment_terms=transaction_data.payment_terms,
            shipping_amount=transaction_data.shipping_amount,
            shipping_address=transaction_data.shipping_address,
            billing_address=transaction_data.billing_address,
            purchase_order_number=transaction_data.purchase_order_number,
            sales_person_id=transaction_data.sales_person_id,
            notes=transaction_data.notes,
            customer_notes=transaction_data.customer_notes
        )
        
        return await transaction_to_response_schema(transaction, repositories, include_items=True)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[SalesTransactionResponseSchema])
async def list_sales_transactions(
    query: SalesTransactionListQuerySchema = Depends(),
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """List sales transactions with filtering and pagination."""
    try:
        # Build filters
        filters = {}
        if query.customer_id:
            filters['customer_id'] = query.customer_id
        if query.status:
            filters['status'] = query.status
        if query.payment_status:
            filters['payment_status'] = query.payment_status
        if query.start_date:
            filters['start_date'] = query.start_date
        if query.end_date:
            filters['end_date'] = query.end_date
        
        # Get transactions
        transactions = await repositories['sales_repository'].list(
            skip=query.skip,
            limit=query.limit,
            filters=filters,
            sort_by=query.sort_by,
            sort_desc=query.sort_desc
        )
        
        # Convert to response schemas
        return [
            await transaction_to_response_schema(t, repositories, include_items=False)
            for t in transactions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}", response_model=SalesTransactionDetailSchema)
async def get_sales_transaction(
    transaction_id: UUID,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get a specific sales transaction by ID."""
    try:
        transaction = await repositories['sales_repository'].get_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sales transaction {transaction_id} not found"
            )
        
        return await transaction_to_response_schema(transaction, repositories, include_items=True)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{transaction_id}", response_model=SalesTransactionResponseSchema)
async def update_sales_transaction(
    transaction_id: UUID,
    update_data: SalesTransactionUpdateSchema,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Update a sales transaction."""
    try:
        transaction = await repositories['sales_repository'].get_by_id(transaction_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sales transaction {transaction_id} not found"
            )
        
        # Update fields if provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(transaction, field) and value is not None:
                setattr(transaction, field, value)
        
        updated = await repositories['sales_repository'].update(transaction)
        return await transaction_to_response_schema(updated, repositories, include_items=False)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{transaction_id}/confirm", response_model=SalesTransactionDetailSchema)
async def confirm_sales_order(
    transaction_id: UUID,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Confirm a draft sales order."""
    try:
        use_case = ConfirmSalesOrderUseCase(
            repositories['sales_repository'],
            repositories['sales_item_repository'],
            repositories['stock_movement_service']
        )
        
        transaction = await use_case.execute(transaction_id)
        return await transaction_to_response_schema(transaction, repositories, include_items=True)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{transaction_id}/payment", response_model=SalesTransactionResponseSchema)
async def update_payment(
    transaction_id: UUID,
    payment_data: UpdatePaymentSchema,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Update payment information for a sales transaction."""
    try:
        use_case = UpdatePaymentUseCase(repositories['sales_repository'])
        
        transaction = await use_case.execute(
            transaction_id=transaction_id,
            amount_paid=payment_data.amount_paid,
            payment_notes=payment_data.payment_notes
        )
        
        return await transaction_to_response_schema(transaction, repositories, include_items=False)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/summary/stats", response_model=SalesSummarySchema)
async def get_sales_summary(
    start_date: datetime = Query(..., description="Start date for summary"),
    end_date: datetime = Query(..., description="End date for summary"),
    group_by: Optional[str] = Query(None, description="Group by: day, week, month"),
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get sales summary statistics for a date range."""
    try:
        summary = await repositories['sales_repository'].get_sales_summary(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )
        
        return SalesSummarySchema(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/overdue", response_model=List[SalesTransactionResponseSchema])
async def get_overdue_transactions(
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get all overdue sales transactions."""
    try:
        transactions = await repositories['sales_repository'].get_overdue_transactions()
        
        return [
            await transaction_to_response_schema(t, repositories, include_items=False)
            for t in transactions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/pending-delivery", response_model=List[SalesTransactionResponseSchema])
async def get_pending_delivery(
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get all sales transactions pending delivery."""
    try:
        transactions = await repositories['sales_repository'].get_pending_delivery()
        
        return [
            await transaction_to_response_schema(t, repositories, include_items=False)
            for t in transactions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))