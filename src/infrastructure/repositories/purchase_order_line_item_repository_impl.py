from typing import List, Optional, Dict
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_

from ...domain.entities.purchase_order_line_item import PurchaseOrderLineItem, WarrantyPeriodType
from ...domain.repositories.purchase_order_line_item_repository import PurchaseOrderLineItemRepository
from ..database.models import PurchaseOrderLineItemModel, WarrantyPeriodType as WarrantyPeriodTypeDB


class SQLAlchemyPurchaseOrderLineItemRepository(PurchaseOrderLineItemRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, line_item: PurchaseOrderLineItem) -> PurchaseOrderLineItem:
        """Save a purchase order line item to the database."""
        # Check if it's an update or insert
        existing = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.id == line_item.id
        ).first()
        
        if existing:
            # Update existing record
            existing.purchase_order_id = line_item.purchase_order_id
            existing.inventory_item_master_id = line_item.inventory_item_master_id
            existing.warehouse_id = line_item.warehouse_id
            existing.quantity = line_item.quantity
            existing.unit_price = float(line_item.unit_price)
            existing.serial_number = line_item.serial_number
            existing.discount = float(line_item.discount)
            existing.tax_amount = float(line_item.tax_amount)
            existing.received_quantity = line_item.received_quantity
            existing.reference_number = line_item.reference_number
            existing.warranty_period_type = line_item.warranty_period_type.value if line_item.warranty_period_type else None
            existing.warranty_period = line_item.warranty_period
            existing.rental_rate = float(line_item.rental_rate)
            existing.replacement_cost = float(line_item.replacement_cost)
            existing.late_fee_rate = float(line_item.late_fee_rate)
            existing.sell_tax_rate = line_item.sell_tax_rate
            existing.rent_tax_rate = line_item.rent_tax_rate
            existing.rentable = line_item.rentable
            existing.sellable = line_item.sellable
            existing.selling_price = float(line_item.selling_price)
            existing.updated_at = line_item.updated_at
            existing.is_active = line_item.is_active
            
            self.session.commit()
            self.session.refresh(existing)
            return self._model_to_entity(existing)
        else:
            # Insert new record
            line_model = PurchaseOrderLineItemModel(
                id=line_item.id,
                purchase_order_id=line_item.purchase_order_id,
                inventory_item_master_id=line_item.inventory_item_master_id,
                warehouse_id=line_item.warehouse_id,
                quantity=line_item.quantity,
                unit_price=float(line_item.unit_price),
                serial_number=line_item.serial_number,
                discount=float(line_item.discount),
                tax_amount=float(line_item.tax_amount),
                received_quantity=line_item.received_quantity,
                reference_number=line_item.reference_number,
                warranty_period_type=line_item.warranty_period_type.value if line_item.warranty_period_type else None,
                warranty_period=line_item.warranty_period,
                rental_rate=float(line_item.rental_rate),
                replacement_cost=float(line_item.replacement_cost),
                late_fee_rate=float(line_item.late_fee_rate),
                sell_tax_rate=line_item.sell_tax_rate,
                rent_tax_rate=line_item.rent_tax_rate,
                rentable=line_item.rentable,
                sellable=line_item.sellable,
                selling_price=float(line_item.selling_price),
                created_at=line_item.created_at,
                updated_at=line_item.updated_at,
                created_by=line_item.created_by,
                is_active=line_item.is_active,
            )
            self.session.add(line_model)
            self.session.commit()
            self.session.refresh(line_model)
            return self._model_to_entity(line_model)

    async def save_many(self, line_items: List[PurchaseOrderLineItem]) -> List[PurchaseOrderLineItem]:
        """Save multiple purchase order line items."""
        saved_items = []
        for line_item in line_items:
            saved_item = await self.save(line_item)
            saved_items.append(saved_item)
        return saved_items

    async def find_by_id(self, line_item_id: UUID) -> Optional[PurchaseOrderLineItem]:
        """Find a line item by its ID."""
        line_model = self.session.query(PurchaseOrderLineItemModel).options(
            joinedload(PurchaseOrderLineItemModel.inventory_item_master),
            joinedload(PurchaseOrderLineItemModel.warehouse)
        ).filter(PurchaseOrderLineItemModel.id == line_item_id).first()
        
        if line_model:
            return self._model_to_entity(line_model)
        return None

    async def find_by_purchase_order(self, purchase_order_id: UUID) -> List[PurchaseOrderLineItem]:
        """Find all line items for a purchase order."""
        line_models = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.purchase_order_id == purchase_order_id
        ).all()
        
        return [self._model_to_entity(model) for model in line_models]

    async def find_by_inventory_item(self, inventory_item_master_id: UUID) -> List[PurchaseOrderLineItem]:
        """Find all line items for an inventory item."""
        line_models = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.inventory_item_master_id == inventory_item_master_id
        ).all()
        
        return [self._model_to_entity(model) for model in line_models]

    async def find_by_warehouse(self, warehouse_id: UUID) -> List[PurchaseOrderLineItem]:
        """Find all line items for a warehouse."""
        line_models = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.warehouse_id == warehouse_id
        ).all()
        
        return [self._model_to_entity(model) for model in line_models]

    async def find_by_serial_number(self, serial_number: str) -> Optional[PurchaseOrderLineItem]:
        """Find a line item by serial number."""
        line_model = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.serial_number == serial_number
        ).first()
        
        if line_model:
            return self._model_to_entity(line_model)
        return None

    async def find_unreceived_items(self, purchase_order_id: Optional[UUID] = None) -> List[PurchaseOrderLineItem]:
        """Find line items that haven't been fully received."""
        query = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.received_quantity < PurchaseOrderLineItemModel.quantity
        )
        
        if purchase_order_id:
            query = query.filter(PurchaseOrderLineItemModel.purchase_order_id == purchase_order_id)
        
        line_models = query.all()
        return [self._model_to_entity(model) for model in line_models]

    async def find_partially_received_items(self, purchase_order_id: Optional[UUID] = None) -> List[PurchaseOrderLineItem]:
        """Find line items that have been partially received."""
        query = self.session.query(PurchaseOrderLineItemModel).filter(
            and_(
                PurchaseOrderLineItemModel.received_quantity > 0,
                PurchaseOrderLineItemModel.received_quantity < PurchaseOrderLineItemModel.quantity
            )
        )
        
        if purchase_order_id:
            query = query.filter(PurchaseOrderLineItemModel.purchase_order_id == purchase_order_id)
        
        line_models = query.all()
        return [self._model_to_entity(model) for model in line_models]

    async def update(self, line_item: PurchaseOrderLineItem) -> PurchaseOrderLineItem:
        """Update an existing line item."""
        return await self.save(line_item)

    async def update_many(self, line_items: List[PurchaseOrderLineItem]) -> List[PurchaseOrderLineItem]:
        """Update multiple line items."""
        return await self.save_many(line_items)

    async def delete(self, line_item_id: UUID) -> bool:
        """Delete a line item by ID."""
        line_model = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.id == line_item_id
        ).first()
        
        if line_model:
            line_model.is_active = False
            self.session.commit()
            return True
        return False

    async def delete_by_purchase_order(self, purchase_order_id: UUID) -> int:
        """Delete all line items for a purchase order. Returns number of deleted items."""
        updated_count = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.purchase_order_id == purchase_order_id
        ).update({"is_active": False})
        
        self.session.commit()
        return updated_count

    async def exists(self, line_item_id: UUID) -> bool:
        """Check if a line item exists by ID."""
        count = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.id == line_item_id
        ).count()
        return count > 0

    async def exists_by_serial_number(self, serial_number: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a line item exists by serial number, optionally excluding a specific ID."""
        query = self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.serial_number == serial_number
        )
        
        if exclude_id:
            query = query.filter(PurchaseOrderLineItemModel.id != exclude_id)
        
        return query.count() > 0

    async def count_by_purchase_order(self, purchase_order_id: UUID) -> int:
        """Count line items for a purchase order."""
        return self.session.query(PurchaseOrderLineItemModel).filter(
            PurchaseOrderLineItemModel.purchase_order_id == purchase_order_id
        ).count()

    async def sum_total_by_purchase_order(self, purchase_order_id: UUID) -> dict:
        """Calculate sum of amounts, tax, and discount for a purchase order."""
        result = self.session.query(
            func.sum(PurchaseOrderLineItemModel.quantity * PurchaseOrderLineItemModel.unit_price - PurchaseOrderLineItemModel.discount).label('total_amount'),
            func.sum(PurchaseOrderLineItemModel.tax_amount).label('total_tax'),
            func.sum(PurchaseOrderLineItemModel.discount).label('total_discount')
        ).filter(
            PurchaseOrderLineItemModel.purchase_order_id == purchase_order_id
        ).first()
        
        return {
            'total_amount': Decimal(str(result.total_amount or 0)),
            'total_tax': Decimal(str(result.total_tax or 0)),
            'total_discount': Decimal(str(result.total_discount or 0))
        }

    def _model_to_entity(self, model: PurchaseOrderLineItemModel) -> PurchaseOrderLineItem:
        """Convert a database model to a domain entity."""
        return PurchaseOrderLineItem(
            purchase_order_id=model.purchase_order_id,
            inventory_item_master_id=model.inventory_item_master_id,
            warehouse_id=model.warehouse_id,
            quantity=model.quantity,
            unit_price=Decimal(str(model.unit_price)),
            serial_number=model.serial_number,
            discount=Decimal(str(model.discount)),
            tax_amount=Decimal(str(model.tax_amount)),
            received_quantity=model.received_quantity,
            reference_number=model.reference_number,
            warranty_period_type=WarrantyPeriodType(model.warranty_period_type) if model.warranty_period_type else None,
            warranty_period=model.warranty_period,
            rental_rate=Decimal(str(model.rental_rate)),
            replacement_cost=Decimal(str(model.replacement_cost)),
            late_fee_rate=Decimal(str(model.late_fee_rate)),
            sell_tax_rate=model.sell_tax_rate,
            rent_tax_rate=model.rent_tax_rate,
            rentable=model.rentable,
            sellable=model.sellable,
            selling_price=Decimal(str(model.selling_price)),
            line_item_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )