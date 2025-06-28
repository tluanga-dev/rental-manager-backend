from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date
from decimal import Decimal

from ...domain.entities.purchase_order import PurchaseOrder, PurchaseOrderStatus
from ...domain.entities.purchase_order_line_item import PurchaseOrderLineItem
from ...domain.repositories.purchase_order_repository import PurchaseOrderRepository
from ...domain.repositories.purchase_order_line_item_repository import PurchaseOrderLineItemRepository
from ...domain.repositories.vendor_repository import VendorRepository
from ...domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from ...infrastructure.database.models import InventoryItemStockMovementModel, MovementType, LineItemModel
from sqlalchemy.orm import Session


class CreatePurchaseOrderUseCase:
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        line_item_repository: PurchaseOrderLineItemRepository,
        vendor_repository: VendorRepository,
        inventory_repository: InventoryItemMasterRepository,
    ) -> None:
        self.purchase_order_repository = purchase_order_repository
        self.line_item_repository = line_item_repository
        self.vendor_repository = vendor_repository
        self.inventory_repository = inventory_repository

    async def execute(
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
        # Validate vendor exists
        vendor = await self.vendor_repository.find_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor with ID {vendor_id} not found")

        # Generate order number
        order_number = await self.purchase_order_repository.get_next_order_number()

        # Create purchase order
        purchase_order = PurchaseOrder(
            order_number=order_number,
            vendor_id=vendor_id,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            reference_number=reference_number,
            invoice_number=invoice_number,
            notes=notes,
            created_by=created_by,
        )

        # Save purchase order
        saved_order = await self.purchase_order_repository.save(purchase_order)

        # Process line items
        total_amount = Decimal("0.00")
        total_tax = Decimal("0.00")
        total_discount = Decimal("0.00")
        
        for item_data in items:
            # Validate inventory item and warehouse
            inventory_item = await self.inventory_repository.find_by_id(item_data["inventory_item_master_id"])
            if not inventory_item:
                raise ValueError(f"Inventory item with ID {item_data['inventory_item_master_id']} not found")
            
            # Note: Warehouse validation could be added here if we have a sync warehouse repository

            # Create line item
            line_item = PurchaseOrderLineItem(
                purchase_order_id=saved_order.id,
                inventory_item_master_id=item_data["inventory_item_master_id"],
                warehouse_id=item_data["warehouse_id"],
                quantity=item_data["quantity"],
                unit_price=Decimal(str(item_data.get("unit_price", 0))),
                serial_number=item_data.get("serial_number"),
                discount=Decimal(str(item_data.get("discount", 0))),
                tax_amount=Decimal(str(item_data.get("tax_amount", 0))),
                reference_number=item_data.get("reference_number"),
                warranty_period_type=item_data.get("warranty_period_type"),
                warranty_period=item_data.get("warranty_period"),
                rental_rate=Decimal(str(item_data.get("rental_rate", 0))),
                replacement_cost=Decimal(str(item_data.get("replacement_cost", 0))),
                late_fee_rate=Decimal(str(item_data.get("late_fee_rate", 0))),
                sell_tax_rate=item_data.get("sell_tax_rate", 0),
                rent_tax_rate=item_data.get("rent_tax_rate", 0),
                rentable=item_data.get("rentable", True),
                sellable=item_data.get("sellable", False),
                selling_price=Decimal(str(item_data.get("selling_price", 0))),
                created_by=created_by,
            )

            # Save line item
            await self.line_item_repository.save(line_item)

            # Update totals
            total_amount += line_item.amount
            total_tax += line_item.tax_amount
            total_discount += line_item.discount

        # Update purchase order totals
        saved_order.update_totals(total_amount, total_tax, total_discount)
        return await self.purchase_order_repository.update(saved_order)


class UpdatePurchaseOrderUseCase:
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        vendor_repository: VendorRepository,
    ) -> None:
        self.purchase_order_repository = purchase_order_repository
        self.vendor_repository = vendor_repository

    async def execute(
        self,
        purchase_order_id: UUID,
        vendor_id: Optional[UUID] = None,
        order_date: Optional[date] = None,
        expected_delivery_date: Optional[date] = None,
        reference_number: Optional[str] = None,
        invoice_number: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> PurchaseOrder:
        # Get purchase order
        purchase_order = await self.purchase_order_repository.find_by_id(purchase_order_id)
        if not purchase_order:
            raise ValueError(f"Purchase order with ID {purchase_order_id} not found")

        # Check if editable
        if not purchase_order.is_editable():
            raise ValueError(f"Purchase order with status {purchase_order.status.value} cannot be edited")

        # Validate new vendor if provided
        if vendor_id and vendor_id != purchase_order.vendor_id:
            vendor = await self.vendor_repository.find_by_id(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor with ID {vendor_id} not found")
            purchase_order._vendor_id = vendor_id

        # Update fields
        if order_date or expected_delivery_date:
            purchase_order.update_dates(order_date, expected_delivery_date)
        
        if reference_number is not None or invoice_number is not None:
            purchase_order.update_references(reference_number, invoice_number)
        
        if notes is not None:
            purchase_order.update_notes(notes)

        return await self.purchase_order_repository.update(purchase_order)


class ReceivePurchaseOrderUseCase:
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        line_item_repository: PurchaseOrderLineItemRepository,
        session: Session,  # Need direct session access for stock movements
    ) -> None:
        self.purchase_order_repository = purchase_order_repository
        self.line_item_repository = line_item_repository
        self.session = session

    async def execute(
        self,
        purchase_order_id: UUID,
        received_items: List[Dict[str, Any]],  # [{"line_item_id": UUID, "quantity": int}]
    ) -> PurchaseOrder:
        # Get purchase order
        purchase_order = await self.purchase_order_repository.find_by_id(purchase_order_id)
        if not purchase_order:
            raise ValueError(f"Purchase order with ID {purchase_order_id} not found")

        # Check if receivable
        if not purchase_order.is_receivable():
            raise ValueError(f"Purchase order with status {purchase_order.status.value} cannot receive items")

        # Process each received item
        all_fully_received = True
        any_received = False

        for item_data in received_items:
            line_item = await self.line_item_repository.find_by_id(item_data["line_item_id"])
            if not line_item:
                raise ValueError(f"Line item with ID {item_data['line_item_id']} not found")
            
            if line_item.purchase_order_id != purchase_order_id:
                raise ValueError(f"Line item {item_data['line_item_id']} does not belong to this purchase order")

            # Record receipt
            line_item.receive_items(item_data["quantity"])
            await self.line_item_repository.update(line_item)

            # Create or update inventory line item
            line_item_model = self.session.query(LineItemModel).filter(
                LineItemModel.inventory_item_master_id == line_item.inventory_item_master_id,
                LineItemModel.warehouse_id == line_item.warehouse_id,
                LineItemModel.serial_number == line_item.serial_number
            ).first()

            if not line_item_model:
                # Create new line item
                line_item_model = LineItemModel(
                    inventory_item_master_id=line_item.inventory_item_master_id,
                    warehouse_id=line_item.warehouse_id,
                    serial_number=line_item.serial_number,
                    quantity=0,
                    rental_rate=float(line_item.rental_rate),
                    replacement_cost=float(line_item.replacement_cost),
                    late_fee_rate=float(line_item.late_fee_rate),
                    sell_tax_rate=line_item.sell_tax_rate,
                    rent_tax_rate=line_item.rent_tax_rate,
                    rentable=line_item.rentable,
                    sellable=line_item.sellable,
                    selling_price=float(line_item.selling_price),
                    warranty_period_type=line_item.warranty_period_type.value if line_item.warranty_period_type else None,
                    warranty_period=line_item.warranty_period,
                )
                self.session.add(line_item_model)
                self.session.flush()

            # Update quantity
            quantity_before = line_item_model.quantity
            line_item_model.quantity += item_data["quantity"]
            quantity_after = line_item_model.quantity

            # Create stock movement record
            movement = InventoryItemStockMovementModel(
                inventory_item_id=line_item_model.id,
                movement_type=MovementType.PURCHASE,
                inventory_transaction_id=purchase_order.order_number,
                quantity=item_data["quantity"],
                quantity_on_hand_before=quantity_before,
                quantity_on_hand_after=quantity_after,
                warehouse_to_id=line_item.warehouse_id,
                notes=f"Purchase order receipt: {purchase_order.order_number}"
            )
            self.session.add(movement)

            # Check if fully received
            if not line_item.is_fully_received():
                all_fully_received = False
            
            any_received = True

        # Update purchase order status
        if all_fully_received:
            purchase_order.mark_as_received()
        elif any_received:
            purchase_order.mark_as_partially_received()

        # Commit all changes
        self.session.commit()

        return await self.purchase_order_repository.update(purchase_order)


class CancelPurchaseOrderUseCase:
    def __init__(self, purchase_order_repository: PurchaseOrderRepository) -> None:
        self.purchase_order_repository = purchase_order_repository

    async def execute(self, purchase_order_id: UUID) -> PurchaseOrder:
        purchase_order = await self.purchase_order_repository.find_by_id(purchase_order_id)
        if not purchase_order:
            raise ValueError(f"Purchase order with ID {purchase_order_id} not found")

        purchase_order.cancel()
        return await self.purchase_order_repository.update(purchase_order)


class GetPurchaseOrderUseCase:
    def __init__(self, purchase_order_repository: PurchaseOrderRepository) -> None:
        self.purchase_order_repository = purchase_order_repository

    async def execute(self, purchase_order_id: UUID) -> Optional[PurchaseOrder]:
        return await self.purchase_order_repository.find_by_id(purchase_order_id)


class GetPurchaseOrderDetailsUseCase:
    def __init__(
        self,
        purchase_order_repository: PurchaseOrderRepository,
        line_item_repository: PurchaseOrderLineItemRepository,
    ) -> None:
        self.purchase_order_repository = purchase_order_repository
        self.line_item_repository = line_item_repository

    async def execute(self, purchase_order_id: UUID) -> Dict[str, Any]:
        purchase_order = await self.purchase_order_repository.find_by_id(purchase_order_id)
        if not purchase_order:
            raise ValueError(f"Purchase order with ID {purchase_order_id} not found")

        line_items = await self.line_item_repository.find_by_purchase_order(purchase_order_id)

        return {
            "purchase_order": purchase_order,
            "line_items": line_items,
            "total_items": len(line_items),
            "items_received": sum(1 for item in line_items if item.is_fully_received()),
            "items_pending": sum(1 for item in line_items if not item.is_fully_received()),
        }


class ListPurchaseOrdersUseCase:
    def __init__(self, purchase_order_repository: PurchaseOrderRepository) -> None:
        self.purchase_order_repository = purchase_order_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        vendor_id: Optional[UUID] = None,
        status: Optional[PurchaseOrderStatus] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[PurchaseOrder]:
        if vendor_id:
            return await self.purchase_order_repository.find_by_vendor(vendor_id, skip, limit)
        elif status:
            return await self.purchase_order_repository.find_by_status(status, skip, limit)
        elif start_date and end_date:
            return await self.purchase_order_repository.find_by_date_range(start_date, end_date, skip, limit)
        else:
            return await self.purchase_order_repository.find_all(skip, limit)


class SearchPurchaseOrdersUseCase:
    def __init__(self, purchase_order_repository: PurchaseOrderRepository) -> None:
        self.purchase_order_repository = purchase_order_repository

    async def execute(
        self,
        query: str,
        search_fields: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[PurchaseOrder]:
        return await self.purchase_order_repository.search_purchase_orders(query, search_fields, limit)