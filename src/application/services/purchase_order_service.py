from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from sqlalchemy.orm import Session

from ...domain.entities.purchase_order import PurchaseOrder, PurchaseOrderStatus
from ...domain.repositories.purchase_order_repository import PurchaseOrderRepository
from ...domain.repositories.purchase_order_line_item_repository import PurchaseOrderLineItemRepository
from ...domain.repositories.vendor_repository import VendorRepository
from ...domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from ..use_cases.purchase_order_use_cases import (
    CreatePurchaseOrderUseCase,
    UpdatePurchaseOrderUseCase,
    ReceivePurchaseOrderUseCase,
    CancelPurchaseOrderUseCase,
    GetPurchaseOrderUseCase,
    GetPurchaseOrderDetailsUseCase,
    ListPurchaseOrdersUseCase,
    SearchPurchaseOrdersUseCase,
)


class PurchaseOrderService:
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        line_item_repository: PurchaseOrderLineItemRepository,
        vendor_repository: VendorRepository,
        inventory_repository: InventoryItemMasterRepository,
        session: Session,
    ) -> None:
        self.purchase_order_repository = purchase_order_repository
        self.line_item_repository = line_item_repository
        self.vendor_repository = vendor_repository
        self.inventory_repository = inventory_repository
        self.session = session
        
        # Initialize use cases
        self.create_purchase_order_use_case = CreatePurchaseOrderUseCase(
            purchase_order_repository,
            line_item_repository,
            vendor_repository,
            inventory_repository,
        )
        self.update_purchase_order_use_case = UpdatePurchaseOrderUseCase(
            purchase_order_repository,
            vendor_repository,
        )
        self.receive_purchase_order_use_case = ReceivePurchaseOrderUseCase(
            purchase_order_repository,
            line_item_repository,
            session,
        )
        self.cancel_purchase_order_use_case = CancelPurchaseOrderUseCase(
            purchase_order_repository
        )
        self.get_purchase_order_use_case = GetPurchaseOrderUseCase(
            purchase_order_repository
        )
        self.get_purchase_order_details_use_case = GetPurchaseOrderDetailsUseCase(
            purchase_order_repository,
            line_item_repository,
        )
        self.list_purchase_orders_use_case = ListPurchaseOrdersUseCase(
            purchase_order_repository
        )
        self.search_purchase_orders_use_case = SearchPurchaseOrdersUseCase(
            purchase_order_repository
        )

    async def create_purchase_order(
        self,
        vendor_id: UUID,
        order_date: date,
        items: List[Dict[str, Any]],
        expected_delivery_date: Optional[date] = None,
        reference_number: Optional[str] = None,
        invoice_number: Optional[str] = None,
        notes: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> PurchaseOrder:
        """Create a new purchase order with line items."""
        return await self.create_purchase_order_use_case.execute(
            vendor_id=vendor_id,
            order_date=order_date,
            items=items,
            expected_delivery_date=expected_delivery_date,
            reference_number=reference_number,
            invoice_number=invoice_number,
            notes=notes,
            created_by=created_by,
        )

    async def update_purchase_order(
        self,
        purchase_order_id: UUID,
        vendor_id: Optional[UUID] = None,
        order_date: Optional[date] = None,
        expected_delivery_date: Optional[date] = None,
        reference_number: Optional[str] = None,
        invoice_number: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> PurchaseOrder:
        """Update an existing purchase order."""
        return await self.update_purchase_order_use_case.execute(
            purchase_order_id=purchase_order_id,
            vendor_id=vendor_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            reference_number=reference_number,
            invoice_number=invoice_number,
            notes=notes,
        )

    async def receive_items(
        self,
        purchase_order_id: UUID,
        received_items: List[Dict[str, Any]],
    ) -> PurchaseOrder:
        """Receive items for a purchase order."""
        return await self.receive_purchase_order_use_case.execute(
            purchase_order_id=purchase_order_id,
            received_items=received_items,
        )

    async def cancel_purchase_order(self, purchase_order_id: UUID) -> PurchaseOrder:
        """Cancel a purchase order."""
        return await self.cancel_purchase_order_use_case.execute(purchase_order_id)

    async def get_purchase_order(self, purchase_order_id: UUID) -> Optional[PurchaseOrder]:
        """Get a purchase order by ID."""
        return await self.get_purchase_order_use_case.execute(purchase_order_id)

    async def get_purchase_order_details(self, purchase_order_id: UUID) -> Dict[str, Any]:
        """Get detailed information about a purchase order including line items."""
        return await self.get_purchase_order_details_use_case.execute(purchase_order_id)

    async def list_purchase_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        vendor_id: Optional[UUID] = None,
        status: Optional[PurchaseOrderStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PurchaseOrder]:
        """List purchase orders with optional filters."""
        return await self.list_purchase_orders_use_case.execute(
            skip=skip,
            limit=limit,
            vendor_id=vendor_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

    async def search_purchase_orders(
        self,
        query: str,
        search_fields: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[PurchaseOrder]:
        """Search purchase orders by query string."""
        return await self.search_purchase_orders_use_case.execute(
            query=query,
            search_fields=search_fields,
            limit=limit,
        )

    async def mark_as_ordered(self, purchase_order_id: UUID) -> PurchaseOrder:
        """Mark a purchase order as ordered."""
        purchase_order = await self.get_purchase_order(purchase_order_id)
        if not purchase_order:
            raise ValueError(f"Purchase order with ID {purchase_order_id} not found")
        
        purchase_order.mark_as_ordered()
        return await self.purchase_order_repository.update(purchase_order)

    async def get_line_items(self, purchase_order_id: UUID) -> List[Dict[str, Any]]:
        """Get all line items for a purchase order."""
        line_items = await self.line_item_repository.find_by_purchase_order(purchase_order_id)
        return [
            {
                "id": str(item.id),
                "inventory_item_master_id": str(item.inventory_item_master_id),
                "warehouse_id": str(item.warehouse_id),
                "quantity": item.quantity,
                "received_quantity": item.received_quantity,
                "unit_price": str(item.unit_price),
                "discount": str(item.discount),
                "tax_amount": str(item.tax_amount),
                "total_price": str(item.total_price),
                "serial_number": item.serial_number,
                "reference_number": item.reference_number,
                "is_fully_received": item.is_fully_received(),
                "remaining_quantity": item.get_remaining_quantity(),
            }
            for item in line_items
        ]

    async def get_purchase_order_summary(self, purchase_order_id: UUID) -> Dict[str, Any]:
        """Get a summary of a purchase order."""
        details = await self.get_purchase_order_details(purchase_order_id)
        purchase_order = details["purchase_order"]
        
        return {
            "order_number": purchase_order.order_number,
            "vendor_id": str(purchase_order.vendor_id),
            "status": purchase_order.status.value,
            "order_date": purchase_order.order_date.isoformat(),
            "expected_delivery_date": (
                purchase_order.expected_delivery_date.isoformat()
                if purchase_order.expected_delivery_date
                else None
            ),
            "grand_total": str(purchase_order.grand_total),
            "total_items": details["total_items"],
            "items_received": details["items_received"],
            "items_pending": details["items_pending"],
            "is_editable": purchase_order.is_editable(),
            "is_receivable": purchase_order.is_receivable(),
        }