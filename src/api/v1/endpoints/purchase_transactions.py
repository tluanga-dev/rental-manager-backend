"""Purchase Transaction API Endpoints

This module defines FastAPI endpoints for purchase transaction operations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.application.services.purchase_transaction_service import PurchaseTransactionService
from src.core.config.database import get_db_session
from src.domain.value_objects.purchase.purchase_status import PurchaseStatus
from src.infrastructure.repositories.purchase_transaction_repository_impl import SQLAlchemyPurchaseTransactionRepository
from src.infrastructure.repositories.purchase_transaction_item_repository_impl import SQLAlchemyPurchaseTransactionItemRepository
from src.infrastructure.repositories.vendor_repository_impl import SQLAlchemyVendorRepository
from src.infrastructure.repositories.inventory_item_master_repository_impl import SQLAlchemyInventoryItemMasterRepository
from src.infrastructure.repositories.warehouse_repository_impl import SQLAlchemyWarehouseRepository
from src.infrastructure.repositories.id_manager_repository_impl import SQLAlchemyIdManagerRepository

from ..schemas.purchase_transaction_schemas import (
    PurchaseTransactionCreateSchema,
    PurchaseTransactionCreateWithItemsSchema,
    PurchaseTransactionUpdateSchema,
    PurchaseTransactionStatusUpdateSchema,
    PurchaseTransactionResponseSchema,
    PurchaseTransactionWithItemsResponseSchema,
    PurchaseTransactionListResponseSchema,
    PurchaseTransactionFiltersSchema,
    PurchaseTransactionSearchSchema,
    PurchaseTransactionStatisticsSchema,
    PurchaseTransactionItemCreateSchema,
    PurchaseTransactionItemUpdateSchema,
    PurchaseTransactionItemResponseSchema,
    PurchaseTransactionItemSummarySchema,
    BulkCreateItemsSchema,
    BulkCreateItemsResponseSchema
)

router = APIRouter(prefix="/purchase-transactions", tags=["purchase-transactions"])


def get_purchase_transaction_service(db: Session = Depends(get_db_session)) -> PurchaseTransactionService:
    """Get purchase transaction service with dependencies."""
    purchase_repository = SQLAlchemyPurchaseTransactionRepository(db)
    purchase_item_repository = SQLAlchemyPurchaseTransactionItemRepository(db)
    vendor_repository = SQLAlchemyVendorRepository(db)
    inventory_repository = SQLAlchemyInventoryItemMasterRepository(db)
    warehouse_repository = SQLAlchemyWarehouseRepository(db)
    id_manager_repository = SQLAlchemyIdManagerRepository(db)
    
    return PurchaseTransactionService(
        purchase_repository=purchase_repository,
        purchase_item_repository=purchase_item_repository,
        vendor_repository=vendor_repository,
        inventory_repository=inventory_repository,
        warehouse_repository=warehouse_repository,
        id_manager_repository=id_manager_repository
    )


def transaction_to_response_schema(transaction) -> PurchaseTransactionResponseSchema:
    """Convert transaction entity to response schema."""
    return PurchaseTransactionResponseSchema(
        id=transaction.id,
        transaction_id=transaction.transaction_id,
        transaction_date=transaction.transaction_date,
        vendor_id=transaction.vendor_id,
        status=transaction.status.value,
        total_amount=transaction.total_amount,
        grand_total=transaction.grand_total,
        purchase_order_number=transaction.purchase_order_number,
        remarks=transaction.remarks,
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
        created_by=transaction.created_by,
        is_active=transaction.is_active
    )


def item_to_response_schema(item) -> PurchaseTransactionItemResponseSchema:
    """Convert item entity to response schema."""
    return PurchaseTransactionItemResponseSchema(
        id=item.id,
        transaction_id=item.transaction_id,
        inventory_item_id=item.inventory_item_id,
        warehouse_id=item.warehouse_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
        discount=item.discount,
        tax_amount=item.tax_amount,
        total_price=item.total_price,
        serial_number=item.serial_number,
        remarks=item.remarks,
        warranty_period_type=item.warranty_period_type,
        warranty_period=item.warranty_period,
        created_at=item.created_at,
        updated_at=item.updated_at,
        created_by=item.created_by,
        is_active=item.is_active
    )


# Transaction endpoints

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: PurchaseTransactionCreateSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Create a new purchase transaction."""
    try:
        transaction = await service.create_transaction(
            vendor_id=transaction_data.vendor_id,
            transaction_date=transaction_data.transaction_date,
            purchase_order_number=transaction_data.purchase_order_number,
            remarks=transaction_data.remarks,
            created_by=transaction_data.created_by
        )
        
        return {
            "transaction": transaction_to_response_schema(transaction),
            "message": "Purchase transaction created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/with-items/", status_code=status.HTTP_201_CREATED)
async def create_transaction_with_items(
    transaction_data: PurchaseTransactionCreateWithItemsSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Create a purchase transaction with items atomically."""
    try:
        # Convert items to dict format
        items = [item.model_dump() for item in transaction_data.items]
        
        transaction = await service.create_transaction_with_items(
            vendor_id=transaction_data.vendor_id,
            transaction_date=transaction_data.transaction_date,
            items=items,
            purchase_order_number=transaction_data.purchase_order_number,
            remarks=transaction_data.remarks,
            created_by=transaction_data.created_by
        )
        
        return {
            "transaction": transaction_to_response_schema(transaction),
            "message": "Purchase transaction with items created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=PurchaseTransactionListResponseSchema)
async def get_transactions(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    vendor_id: Optional[UUID] = Query(None, description="Filter by vendor ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[str] = Query(None, description="Filter by date from (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (YYYY-MM-DD)"),
    purchase_order_number: Optional[str] = Query(None, description="Filter by purchase order number"),
    sort_by: Optional[str] = Query(None, description="Sort by field"),
    sort_desc: bool = Query(True, description="Sort in descending order"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionListResponseSchema:
    """Get purchase transactions with filtering and pagination."""
    try:
        # Convert date strings to date objects
        date_from_obj = None
        date_to_obj = None
        
        if date_from:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, "%Y-%m-%d").date()
        
        if date_to:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, "%Y-%m-%d").date()
        
        result = await service.list_transactions(
            page=page,
            page_size=page_size,
            vendor_id=vendor_id,
            status=status,
            date_from=date_from_obj,
            date_to=date_to_obj,
            purchase_order_number=purchase_order_number,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        transactions = [transaction_to_response_schema(t) for t in result["transactions"]]
        
        return PurchaseTransactionListResponseSchema(
            transactions=transactions,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}/", response_model=PurchaseTransactionWithItemsResponseSchema)
async def get_transaction(
    transaction_id: UUID,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionWithItemsResponseSchema:
    """Get a purchase transaction with its items."""
    try:
        result = await service.get_transaction_with_items(transaction_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase transaction not found")
        
        transaction_response = transaction_to_response_schema(result["transaction"])
        items_response = [item_to_response_schema(item) for item in result["items"]]
        
        return PurchaseTransactionWithItemsResponseSchema(
            **transaction_response.model_dump(),
            items=items_response,
            item_summary=result["item_summary"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/by-transaction-id/{transaction_id}/", response_model=PurchaseTransactionWithItemsResponseSchema)
async def get_transaction_by_transaction_id(
    transaction_id: str,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionWithItemsResponseSchema:
    """Get a purchase transaction by transaction ID."""
    try:
        transaction = await service.get_transaction_by_transaction_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase transaction not found")
        
        result = await service.get_transaction_with_items(transaction.id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase transaction not found")
        
        transaction_response = transaction_to_response_schema(result["transaction"])
        items_response = [item_to_response_schema(item) for item in result["items"]]
        
        return PurchaseTransactionWithItemsResponseSchema(
            **transaction_response.model_dump(),
            items=items_response,
            item_summary=result["item_summary"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{transaction_id}/")
async def update_transaction(
    transaction_id: UUID,
    transaction_data: PurchaseTransactionUpdateSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Update a purchase transaction."""
    try:
        transaction = await service.update_transaction(
            transaction_id=transaction_id,
            vendor_id=transaction_data.vendor_id,
            transaction_date=transaction_data.transaction_date,
            purchase_order_number=transaction_data.purchase_order_number,
            remarks=transaction_data.remarks
        )
        
        return {
            "transaction": transaction_to_response_schema(transaction),
            "message": "Purchase transaction updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{transaction_id}/status/")
async def update_transaction_status(
    transaction_id: UUID,
    status_data: PurchaseTransactionStatusUpdateSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Update purchase transaction status."""
    try:
        new_status = PurchaseStatus(status_data.status)
        transaction = await service.update_transaction_status(transaction_id, new_status)
        
        return {
            "transaction": transaction_to_response_schema(transaction),
            "message": f"Purchase transaction status updated to {new_status.value}"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{transaction_id}/")
async def delete_transaction(
    transaction_id: UUID,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Delete (soft delete) a purchase transaction."""
    try:
        deleted = await service.delete_transaction(transaction_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase transaction not found")
        
        return {
            "message": "Purchase transaction deleted successfully",
            "transaction_id": str(transaction_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/search/", response_model=PurchaseTransactionListResponseSchema)
async def search_transactions(
    search_data: PurchaseTransactionSearchSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionListResponseSchema:
    """Search purchase transactions."""
    try:
        transactions = await service.search_transactions(
            query=search_data.query,
            vendor_id=search_data.vendor_id,
            status=search_data.status
        )
        
        # Limit results
        transactions = transactions[:search_data.limit]
        
        transaction_responses = [transaction_to_response_schema(t) for t in transactions]
        
        return PurchaseTransactionListResponseSchema(
            transactions=transaction_responses,
            total=len(transaction_responses),
            page=1,
            page_size=len(transaction_responses),
            total_pages=1
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}/summary/", response_model=PurchaseTransactionItemSummarySchema)
async def get_transaction_summary(
    transaction_id: UUID,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionItemSummarySchema:
    """Get purchase transaction item summary."""
    try:
        summary = await service.get_item_summary(transaction_id)
        return PurchaseTransactionItemSummarySchema(**summary)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/summary/", response_model=PurchaseTransactionStatisticsSchema)
async def get_transaction_statistics(
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionStatisticsSchema:
    """Get purchase transaction statistics."""
    try:
        stats = await service.get_statistics()
        return PurchaseTransactionStatisticsSchema(**stats)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# Transaction item endpoints

@router.get("/{transaction_id}/items/")
async def get_transaction_items(
    transaction_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Get items for a purchase transaction."""
    try:
        result = await service.get_items_by_transaction(transaction_id, page, page_size)
        items_response = [item_to_response_schema(item) for item in result["items"]]
        
        return {
            "items": items_response,
            "total": result["total"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total_pages": result["total_pages"]
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}/items/{item_id}/", response_model=PurchaseTransactionItemResponseSchema)
async def get_transaction_item(
    transaction_id: UUID,
    item_id: UUID,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> PurchaseTransactionItemResponseSchema:
    """Get a specific transaction item."""
    try:
        item = await service.get_item(item_id)
        if not item or item.transaction_id != transaction_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction item not found")
        
        return item_to_response_schema(item)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{transaction_id}/items/")
async def create_transaction_item(
    transaction_id: UUID,
    item_data: PurchaseTransactionItemCreateSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Create a new transaction item."""
    try:
        item = await service.create_item(
            transaction_id=transaction_id,
            item_master_id=item_data.item_master_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            warehouse_id=item_data.warehouse_id,
            serial_number=item_data.serial_number,
            discount=item_data.discount,
            tax_amount=item_data.tax_amount,
            remarks=item_data.remarks,
            warranty_period_type=item_data.warranty_period_type,
            warranty_period=item_data.warranty_period
        )
        
        return {
            "item": item_to_response_schema(item),
            "message": "Transaction item created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{transaction_id}/items/bulk/", response_model=BulkCreateItemsResponseSchema)
async def bulk_create_transaction_items(
    transaction_id: UUID,
    bulk_data: BulkCreateItemsSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> BulkCreateItemsResponseSchema:
    """Create multiple transaction items atomically."""
    try:
        items_data = [item.model_dump() for item in bulk_data.items]
        created_items = await service.bulk_create_items(transaction_id, items_data)
        
        items_response = [item_to_response_schema(item) for item in created_items]
        
        # Get updated transaction totals
        transaction = await service.get_transaction(transaction_id)
        
        return BulkCreateItemsResponseSchema(
            created_items=items_response,
            total_created=len(created_items),
            total_requested=len(bulk_data.items),
            transaction_id=transaction_id,
            updated_totals={
                "total_amount": transaction.total_amount,
                "grand_total": transaction.grand_total
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{transaction_id}/items/{item_id}/")
async def update_transaction_item(
    transaction_id: UUID,
    item_id: UUID,
    item_data: PurchaseTransactionItemUpdateSchema,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Update a transaction item."""
    try:
        item = await service.update_item(
            item_id=item_id,
            unit_price=item_data.unit_price,
            discount=item_data.discount,
            tax_amount=item_data.tax_amount,
            remarks=item_data.remarks,
            warranty_period_type=item_data.warranty_period_type,
            warranty_period=item_data.warranty_period
        )
        
        return {
            "item": item_to_response_schema(item),
            "message": "Transaction item updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{transaction_id}/items/{item_id}/")
async def delete_transaction_item(
    transaction_id: UUID,
    item_id: UUID,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Delete a transaction item."""
    try:
        deleted = await service.delete_item(item_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction item not found")
        
        return {
            "message": "Transaction item deleted successfully",
            "item_id": str(item_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}/items/{item_id}/summary/")
async def get_transaction_item_summary(
    transaction_id: UUID,
    item_id: UUID,
    service: PurchaseTransactionService = Depends(get_purchase_transaction_service)
) -> Dict[str, Any]:
    """Get transaction item summary (placeholder endpoint for frontend compatibility)."""
    try:
        item = await service.get_item(item_id)
        if not item or item.transaction_id != transaction_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction item not found")
        
        return {
            "item": item_to_response_schema(item),
            "summary": {
                "total_price": item.total_price,
                "discount": item.discount,
                "tax_amount": item.tax_amount,
                "has_warranty": item.has_warranty,
                "serial_count": len(item.serial_number)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))