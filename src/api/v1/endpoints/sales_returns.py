"""Sales Returns API Endpoints

This module defines the FastAPI endpoints for sales return operations.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....core.config.database import get_db_session
from ....application.use_cases.sales import ProcessSalesReturnUseCase
from ....infrastructure.repositories.sales_transaction_repository_impl import SQLAlchemySalesTransactionRepository
from ....infrastructure.repositories.sales_transaction_item_repository_impl import SQLAlchemySalesTransactionItemRepository
from ....infrastructure.repositories.sales_return_repository_impl import SQLAlchemySalesReturnRepository
from ....infrastructure.repositories.sales_return_item_repository_impl import SQLAlchemySalesReturnItemRepository
from ....infrastructure.repositories.id_manager_repository_impl import SQLAlchemyIdManagerRepository
from ....infrastructure.repositories.inventory_stock_movement_service import InventoryStockMovementService
from ..schemas.sales import (
    SalesReturnCreateSchema,
    SalesReturnUpdateSchema,
    SalesReturnResponseSchema,
    SalesReturnDetailSchema,
    SalesReturnListQuerySchema,
    ApproveReturnSchema,
    ReturnSummarySchema
)

router = APIRouter(prefix="/sales/returns", tags=["sales-returns"])


def get_repositories(db: Session = Depends(get_db_session)) -> Dict[str, Any]:
    """Get all required repositories."""
    return {
        'sales_repository': SQLAlchemySalesTransactionRepository(db),
        'sales_item_repository': SQLAlchemySalesTransactionItemRepository(db),
        'return_repository': SQLAlchemySalesReturnRepository(db),
        'return_item_repository': SQLAlchemySalesReturnItemRepository(db),
        'id_manager_repository': SQLAlchemyIdManagerRepository(db),
        'stock_movement_service': InventoryStockMovementService(db)
    }


async def return_to_response_schema(
    sales_return,
    repositories: Dict[str, Any],
    include_items: bool = False
) -> SalesReturnResponseSchema:
    """Convert return entity to response schema."""
    # Get transaction details
    transaction = await repositories['sales_repository'].get_by_id(sales_return.sales_transaction_id)
    
    response_data = {
        'id': sales_return.id,
        'return_id': sales_return.return_id,
        'sales_transaction_id': sales_return.sales_transaction_id,
        'sales_transaction': {
            'id': transaction.id,
            'transaction_id': transaction.transaction_id,
            'customer_id': transaction.customer_id,
            'order_date': transaction.order_date,
            'grand_total': transaction.grand_total
        } if transaction else None,
        'return_date': sales_return.return_date,
        'reason': sales_return.reason,
        'approved_by_id': sales_return.approved_by_id,
        'approved_by_name': None,  # Would need user service
        'refund_amount': sales_return.refund_amount,
        'restocking_fee': sales_return.restocking_fee,
        'net_refund_amount': sales_return.net_refund_amount,
        'is_approved': sales_return.is_approved,
        'created_at': sales_return.created_at,
        'updated_at': sales_return.updated_at,
        'created_by': sales_return.created_by,
        'is_active': sales_return.is_active
    }
    
    if include_items:
        # Get return items
        items = await repositories['return_item_repository'].get_by_return(sales_return.id)
        items_data = []
        
        for item in items:
            # Get sales item details
            sales_item = await repositories['sales_item_repository'].get_by_id(item.sales_item_id)
            
            items_data.append({
                'id': item.id,
                'sales_return_id': item.sales_return_id,
                'sales_item_id': item.sales_item_id,
                'sales_item': {
                    'id': sales_item.id,
                    'inventory_item_master_id': sales_item.inventory_item_master_id,
                    'quantity': sales_item.quantity,
                    'unit_price': sales_item.unit_price,
                    'total': sales_item.total
                } if sales_item else None,
                'quantity': item.quantity,
                'condition': item.condition,
                'serial_numbers': item.serial_numbers,
                'is_resellable': item.is_resellable(),
                'created_at': item.created_at,
                'updated_at': item.updated_at,
                'created_by': item.created_by,
                'is_active': item.is_active
            })
        
        return SalesReturnDetailSchema(**response_data, items=items_data)
    
    return SalesReturnResponseSchema(**response_data)


@router.post("/", response_model=SalesReturnDetailSchema, status_code=status.HTTP_201_CREATED)
async def create_sales_return(
    return_data: SalesReturnCreateSchema,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Create a new sales return."""
    try:
        use_case = ProcessSalesReturnUseCase(**repositories)
        
        sales_return = await use_case.execute(
            sales_transaction_id=return_data.sales_transaction_id,
            reason=return_data.reason,
            items=[item.dict() for item in return_data.items],
            restocking_fee=return_data.restocking_fee
        )
        
        return await return_to_response_schema(sales_return, repositories, include_items=True)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[SalesReturnResponseSchema])
async def list_sales_returns(
    query: SalesReturnListQuerySchema = Depends(),
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """List sales returns with filtering and pagination."""
    try:
        # Build filters
        filters = {}
        if query.sales_transaction_id:
            filters['sales_transaction_id'] = query.sales_transaction_id
        if query.approved_by_id:
            filters['approved_by_id'] = query.approved_by_id
        if query.start_date:
            filters['start_date'] = query.start_date
        if query.end_date:
            filters['end_date'] = query.end_date
        
        # Get returns
        returns = await repositories['return_repository'].list(
            skip=query.skip,
            limit=query.limit,
            filters=filters,
            sort_by=query.sort_by,
            sort_desc=query.sort_desc
        )
        
        # Convert to response schemas
        return [
            await return_to_response_schema(r, repositories, include_items=False)
            for r in returns
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{return_id}", response_model=SalesReturnDetailSchema)
async def get_sales_return(
    return_id: str,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get a specific sales return by ID."""
    try:
        sales_return = await repositories['return_repository'].get_by_id(return_id)
        if not sales_return:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sales return {return_id} not found"
            )
        
        return await return_to_response_schema(sales_return, repositories, include_items=True)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{return_id}", response_model=SalesReturnResponseSchema)
async def update_sales_return(
    return_id: str,
    update_data: SalesReturnUpdateSchema,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Update a sales return."""
    try:
        sales_return = await repositories['return_repository'].get_by_id(return_id)
        if not sales_return:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sales return {return_id} not found"
            )
        
        # Check if already approved
        if sales_return.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update an approved return"
            )
        
        # Update fields if provided
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(sales_return, field) and value is not None:
                setattr(sales_return, field, value)
        
        updated = await repositories['return_repository'].update(sales_return)
        return await return_to_response_schema(updated, repositories, include_items=False)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{return_id}/approve", response_model=SalesReturnResponseSchema)
async def approve_sales_return(
    return_id: str,
    approve_data: ApproveReturnSchema,
    repositories: Dict[str, Any] = Depends(get_repositories),
    # In real app, get current user from auth
    current_user_id: str = Query(..., description="Current user ID")
):
    """Approve a sales return."""
    try:
        sales_return = await repositories['return_repository'].approve(
            return_id=return_id,
            approved_by_id=current_user_id
        )
        
        # Add notes if provided
        if approve_data.notes:
            sales_return.reason = f"{sales_return.reason}\n\nApproval notes: {approve_data.notes}"
            await repositories['return_repository'].update(sales_return)
        
        return await return_to_response_schema(sales_return, repositories, include_items=False)
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/summary/stats", response_model=ReturnSummarySchema)
async def get_return_summary(
    start_date: datetime = Query(..., description="Start date for summary"),
    end_date: datetime = Query(..., description="End date for summary"),
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get return summary statistics for a date range."""
    try:
        summary = await repositories['return_repository'].get_return_summary(
            start_date=start_date,
            end_date=end_date
        )
        
        return ReturnSummarySchema(**summary)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/pending-approval", response_model=List[SalesReturnResponseSchema])
async def get_pending_approval_returns(
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get all sales returns pending approval."""
    try:
        returns = await repositories['return_repository'].get_pending_approval()
        
        return [
            await return_to_response_schema(r, repositories, include_items=False)
            for r in returns
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/by-transaction/{transaction_id}", response_model=List[SalesReturnResponseSchema])
async def get_returns_by_transaction(
    transaction_id: str,
    repositories: Dict[str, Any] = Depends(get_repositories)
):
    """Get all returns for a specific sales transaction."""
    try:
        returns = await repositories['return_repository'].get_by_transaction(transaction_id)
        
        return [
            await return_to_response_schema(r, repositories, include_items=False)
            for r in returns
        ]
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))