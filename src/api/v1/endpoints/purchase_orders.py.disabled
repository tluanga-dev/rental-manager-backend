from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ....application.services.purchase_order_service import PurchaseOrderService
from ....core.config.database import get_db_session
from ....infrastructure.repositories.purchase_order_repository_impl import SQLAlchemyPurchaseOrderRepository
from ....infrastructure.repositories.purchase_order_line_item_repository_impl import SQLAlchemyPurchaseOrderLineItemRepository
from ....infrastructure.repositories.vendor_repository_impl import SQLAlchemyVendorRepository
from ....infrastructure.repositories.inventory_item_master_repository_impl import SQLAlchemyInventoryItemMasterRepository
from ....domain.entities.purchase_order import PurchaseOrderStatus as DomainPurchaseOrderStatus
from ..schemas.purchase_order_schemas import (
    PurchaseOrderCreateSchema,
    PurchaseOrderUpdateSchema,
    PurchaseOrderReceiveSchema,
    PurchaseOrderResponseSchema,
    PurchaseOrderDetailResponseSchema,
    PurchaseOrderListQuerySchema,
    PurchaseOrderSearchQuerySchema,
    PurchaseOrderSummaryResponseSchema,
    PurchaseOrderStatus,
)

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


def get_purchase_order_service(db: Session = Depends(get_db_session)) -> PurchaseOrderService:
    purchase_order_repository = SQLAlchemyPurchaseOrderRepository(db)
    line_item_repository = SQLAlchemyPurchaseOrderLineItemRepository(db)
    vendor_repository = SQLAlchemyVendorRepository(db)
    inventory_repository = SQLAlchemyInventoryItemMasterRepository(db)
    
    return PurchaseOrderService(
        purchase_order_repository,
        line_item_repository,
        vendor_repository,
        inventory_repository,
        db,
    )


def purchase_order_to_response_schema(purchase_order) -> PurchaseOrderResponseSchema:
    return PurchaseOrderResponseSchema(
        id=purchase_order.id,
        order_number=purchase_order.order_number,
        vendor_id=purchase_order.vendor_id,
        order_date=purchase_order.order_date,
        expected_delivery_date=purchase_order.expected_delivery_date,
        status=purchase_order.status.value,
        total_amount=purchase_order.total_amount,
        total_tax_amount=purchase_order.total_tax_amount,
        total_discount=purchase_order.total_discount,
        grand_total=purchase_order.grand_total,
        reference_number=purchase_order.reference_number,
        invoice_number=purchase_order.invoice_number,
        notes=purchase_order.notes,
        created_at=purchase_order.created_at,
        updated_at=purchase_order.updated_at,
        created_by=purchase_order.created_by,
        is_active=purchase_order.is_active,
    )


@router.post("/", response_model=PurchaseOrderResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    purchase_order_data: PurchaseOrderCreateSchema,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Create a new purchase order with line items."""
    try:
        # Convert line items to dict format
        items = [
            {
                "inventory_item_master_id": item.inventory_item_master_id,
                "warehouse_id": item.warehouse_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "serial_number": item.serial_number,
                "discount": item.discount,
                "tax_amount": item.tax_amount,
                "reference_number": item.reference_number,
                "warranty_period_type": item.warranty_period_type,
                "warranty_period": item.warranty_period,
                "rental_rate": item.rental_rate,
                "replacement_cost": item.replacement_cost,
                "late_fee_rate": item.late_fee_rate,
                "sell_tax_rate": item.sell_tax_rate,
                "rent_tax_rate": item.rent_tax_rate,
                "rentable": item.rentable,
                "sellable": item.sellable,
                "selling_price": item.selling_price,
            }
            for item in purchase_order_data.items
        ]
        
        purchase_order = await purchase_order_service.create_purchase_order(
            vendor_id=purchase_order_data.vendor_id,
            order_date=purchase_order_data.order_date,
            items=items,
            expected_delivery_date=purchase_order_data.expected_delivery_date,
            reference_number=purchase_order_data.reference_number,
            invoice_number=purchase_order_data.invoice_number,
            notes=purchase_order_data.notes,
            created_by=purchase_order_data.created_by,
        )
        return purchase_order_to_response_schema(purchase_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create purchase order")


@router.get("/{purchase_order_id}", response_model=PurchaseOrderDetailResponseSchema)
async def get_purchase_order(
    purchase_order_id: UUID,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Get a purchase order by ID with details."""
    try:
        details = await purchase_order_service.get_purchase_order_details(purchase_order_id)
        purchase_order = details["purchase_order"]
        line_items = details["line_items"]
        
        # Get vendor name
        vendor_service = purchase_order_service.vendor_repository
        vendor = await vendor_service.find_by_id(purchase_order.vendor_id)
        vendor_name = vendor.name if vendor else None
        
        return PurchaseOrderDetailResponseSchema(
            id=purchase_order.id,
            order_number=purchase_order.order_number,
            vendor_id=purchase_order.vendor_id,
            vendor_name=vendor_name,
            order_date=purchase_order.order_date,
            expected_delivery_date=purchase_order.expected_delivery_date,
            status=purchase_order.status.value,
            total_amount=purchase_order.total_amount,
            total_tax_amount=purchase_order.total_tax_amount,
            total_discount=purchase_order.total_discount,
            grand_total=purchase_order.grand_total,
            reference_number=purchase_order.reference_number,
            invoice_number=purchase_order.invoice_number,
            notes=purchase_order.notes,
            created_at=purchase_order.created_at,
            updated_at=purchase_order.updated_at,
            created_by=purchase_order.created_by,
            is_active=purchase_order.is_active,
            line_items=[
                {
                    "id": item.id,
                    "purchase_order_id": item.purchase_order_id,
                    "inventory_item_master_id": item.inventory_item_master_id,
                    "warehouse_id": item.warehouse_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "serial_number": item.serial_number,
                    "discount": item.discount,
                    "tax_amount": item.tax_amount,
                    "received_quantity": item.received_quantity,
                    "reference_number": item.reference_number,
                    "warranty_period_type": item.warranty_period_type,
                    "warranty_period": item.warranty_period,
                    "rental_rate": item.rental_rate,
                    "replacement_cost": item.replacement_cost,
                    "late_fee_rate": item.late_fee_rate,
                    "sell_tax_rate": item.sell_tax_rate,
                    "rent_tax_rate": item.rent_tax_rate,
                    "rentable": item.rentable,
                    "sellable": item.sellable,
                    "selling_price": item.selling_price,
                    "amount": item.amount,
                    "total_price": item.total_price,
                    "is_fully_received": item.is_fully_received(),
                    "remaining_quantity": item.get_remaining_quantity(),
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                    "created_by": item.created_by,
                    "is_active": item.is_active,
                }
                for item in line_items
            ],
            total_items=details["total_items"],
            items_received=details["items_received"],
            items_pending=details["items_pending"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve purchase order")


@router.put("/{purchase_order_id}", response_model=PurchaseOrderResponseSchema)
async def update_purchase_order(
    purchase_order_id: UUID,
    update_data: PurchaseOrderUpdateSchema,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Update an existing purchase order."""
    try:
        purchase_order = await purchase_order_service.update_purchase_order(
            purchase_order_id=purchase_order_id,
            vendor_id=update_data.vendor_id,
            order_date=update_data.order_date,
            expected_delivery_date=update_data.expected_delivery_date,
            reference_number=update_data.reference_number,
            invoice_number=update_data.invoice_number,
            notes=update_data.notes,
        )
        return purchase_order_to_response_schema(purchase_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update purchase order")


@router.post("/{purchase_order_id}/receive", response_model=PurchaseOrderResponseSchema)
async def receive_purchase_order_items(
    purchase_order_id: UUID,
    receive_data: PurchaseOrderReceiveSchema,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Receive items for a purchase order."""
    try:
        # Convert to dict format
        received_items = [
            {
                "line_item_id": item.line_item_id,
                "quantity": item.quantity,
            }
            for item in receive_data.received_items
        ]
        
        purchase_order = await purchase_order_service.receive_items(
            purchase_order_id=purchase_order_id,
            received_items=received_items,
        )
        return purchase_order_to_response_schema(purchase_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to receive items")


@router.post("/{purchase_order_id}/mark-as-ordered", response_model=PurchaseOrderResponseSchema)
async def mark_purchase_order_as_ordered(
    purchase_order_id: UUID,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Mark a purchase order as ordered."""
    try:
        purchase_order = await purchase_order_service.mark_as_ordered(purchase_order_id)
        return purchase_order_to_response_schema(purchase_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update purchase order status")


@router.post("/{purchase_order_id}/cancel", response_model=PurchaseOrderResponseSchema)
async def cancel_purchase_order(
    purchase_order_id: UUID,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Cancel a purchase order."""
    try:
        purchase_order = await purchase_order_service.cancel_purchase_order(purchase_order_id)
        return purchase_order_to_response_schema(purchase_order)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to cancel purchase order")


@router.get("/", response_model=List[PurchaseOrderResponseSchema])
async def list_purchase_orders(
    query_params: PurchaseOrderListQuerySchema = Depends(),
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """List purchase orders with optional filters."""
    try:
        # Convert string status to domain enum if provided
        status = DomainPurchaseOrderStatus(query_params.status.value) if query_params.status else None
        
        purchase_orders = await purchase_order_service.list_purchase_orders(
            skip=query_params.skip,
            limit=query_params.limit,
            vendor_id=query_params.vendor_id,
            status=status,
            start_date=query_params.start_date,
            end_date=query_params.end_date,
        )
        return [purchase_order_to_response_schema(po) for po in purchase_orders]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to list purchase orders")


@router.post("/search", response_model=List[PurchaseOrderResponseSchema])
async def search_purchase_orders(
    search_params: PurchaseOrderSearchQuerySchema,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Search purchase orders."""
    try:
        purchase_orders = await purchase_order_service.search_purchase_orders(
            query=search_params.query,
            search_fields=search_params.search_fields,
            limit=search_params.limit,
        )
        return [purchase_order_to_response_schema(po) for po in purchase_orders]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search purchase orders")


@router.get("/{purchase_order_id}/summary", response_model=PurchaseOrderSummaryResponseSchema)
async def get_purchase_order_summary(
    purchase_order_id: UUID,
    purchase_order_service: PurchaseOrderService = Depends(get_purchase_order_service),
):
    """Get a summary of a purchase order."""
    try:
        summary = await purchase_order_service.get_purchase_order_summary(purchase_order_id)
        return PurchaseOrderSummaryResponseSchema(**summary)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to get purchase order summary")