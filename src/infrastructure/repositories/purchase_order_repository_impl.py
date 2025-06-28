from typing import List, Optional
from uuid import UUID
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_

from ...domain.entities.purchase_order import PurchaseOrder, PurchaseOrderStatus
from ...domain.repositories.purchase_order_repository import PurchaseOrderRepository
from ..database.models import PurchaseOrderModel, PurchaseOrderStatus as PurchaseOrderStatusDB


class SQLAlchemyPurchaseOrderRepository(PurchaseOrderRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    async def save(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Save a purchase order entity to the database."""
        # Check if it's an update or insert
        existing = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.id == purchase_order.id
        ).first()
        
        if existing:
            # Update existing record
            existing.order_number = purchase_order.order_number
            existing.vendor_id = purchase_order.vendor_id
            existing.order_date = purchase_order.order_date
            existing.expected_delivery_date = purchase_order.expected_delivery_date
            existing.status = purchase_order.status.value
            existing.total_amount = float(purchase_order.total_amount)
            existing.total_tax_amount = float(purchase_order.total_tax_amount)
            existing.total_discount = float(purchase_order.total_discount)
            existing.grand_total = float(purchase_order.grand_total)
            existing.reference_number = purchase_order.reference_number
            existing.invoice_number = purchase_order.invoice_number
            existing.notes = purchase_order.notes
            existing.updated_at = purchase_order.updated_at
            existing.is_active = purchase_order.is_active
            
            self.session.commit()
            self.session.refresh(existing)
            return self._model_to_entity(existing)
        else:
            # Insert new record
            po_model = PurchaseOrderModel(
                id=purchase_order.id,
                order_number=purchase_order.order_number,
                vendor_id=purchase_order.vendor_id,
                order_date=purchase_order.order_date,
                expected_delivery_date=purchase_order.expected_delivery_date,
                status=purchase_order.status.value,
                total_amount=float(purchase_order.total_amount),
                total_tax_amount=float(purchase_order.total_tax_amount),
                total_discount=float(purchase_order.total_discount),
                grand_total=float(purchase_order.grand_total),
                reference_number=purchase_order.reference_number,
                invoice_number=purchase_order.invoice_number,
                notes=purchase_order.notes,
                created_at=purchase_order.created_at,
                updated_at=purchase_order.updated_at,
                created_by=purchase_order.created_by,
                is_active=purchase_order.is_active,
            )
            self.session.add(po_model)
            self.session.commit()
            self.session.refresh(po_model)
            return self._model_to_entity(po_model)

    async def find_by_id(self, purchase_order_id: UUID) -> Optional[PurchaseOrder]:
        """Find a purchase order by its ID."""
        po_model = self.session.query(PurchaseOrderModel).options(
            joinedload(PurchaseOrderModel.vendor)
        ).filter(PurchaseOrderModel.id == purchase_order_id).first()
        
        if po_model:
            return self._model_to_entity(po_model)
        return None

    async def find_by_order_number(self, order_number: str) -> Optional[PurchaseOrder]:
        """Find a purchase order by its order number."""
        po_model = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.order_number == order_number
        ).first()
        
        if po_model:
            return self._model_to_entity(po_model)
        return None

    async def find_by_vendor(self, vendor_id: UUID, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find purchase orders by vendor ID."""
        po_models = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.vendor_id == vendor_id
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in po_models]

    async def find_by_status(self, status: PurchaseOrderStatus, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find purchase orders by status."""
        po_models = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.status == status.value
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in po_models]

    async def find_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find purchase orders within a date range."""
        po_models = self.session.query(PurchaseOrderModel).filter(
            and_(
                PurchaseOrderModel.order_date >= start_date,
                PurchaseOrderModel.order_date <= end_date
            )
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in po_models]

    async def find_by_reference_number(self, reference_number: str) -> List[PurchaseOrder]:
        """Find purchase orders by reference number."""
        po_models = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.reference_number.ilike(f"%{reference_number}%")
        ).all()
        
        return [self._model_to_entity(model) for model in po_models]

    async def find_by_invoice_number(self, invoice_number: str) -> List[PurchaseOrder]:
        """Find purchase orders by invoice number."""
        po_models = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.invoice_number.ilike(f"%{invoice_number}%")
        ).all()
        
        return [self._model_to_entity(model) for model in po_models]

    async def search_purchase_orders(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[PurchaseOrder]:
        """Search purchase orders across multiple fields."""
        if search_fields is None:
            search_fields = ["order_number", "reference_number", "invoice_number", "notes"]
        
        query_filters = []
        if "order_number" in search_fields:
            query_filters.append(PurchaseOrderModel.order_number.ilike(f"%{query}%"))
        if "reference_number" in search_fields:
            query_filters.append(PurchaseOrderModel.reference_number.ilike(f"%{query}%"))
        if "invoice_number" in search_fields:
            query_filters.append(PurchaseOrderModel.invoice_number.ilike(f"%{query}%"))
        if "notes" in search_fields:
            query_filters.append(PurchaseOrderModel.notes.ilike(f"%{query}%"))
        
        if query_filters:
            from sqlalchemy import or_
            po_models = self.session.query(PurchaseOrderModel).filter(
                or_(*query_filters)
            ).limit(limit).all()
            return [self._model_to_entity(model) for model in po_models]
        
        return []

    async def find_all(self, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find all purchase orders with pagination."""
        po_models = self.session.query(PurchaseOrderModel).offset(skip).limit(limit).all()
        return [self._model_to_entity(model) for model in po_models]

    async def update(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Update an existing purchase order."""
        return await self.save(purchase_order)

    async def delete(self, purchase_order_id: UUID) -> bool:
        """Delete a purchase order by ID (soft delete)."""
        po_model = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.id == purchase_order_id
        ).first()
        
        if po_model:
            po_model.is_active = False
            self.session.commit()
            return True
        return False

    async def exists(self, purchase_order_id: UUID) -> bool:
        """Check if a purchase order exists by ID."""
        count = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.id == purchase_order_id
        ).count()
        return count > 0

    async def exists_by_order_number(self, order_number: str) -> bool:
        """Check if a purchase order exists by order number."""
        count = self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.order_number == order_number
        ).count()
        return count > 0

    async def count_by_status(self, status: PurchaseOrderStatus) -> int:
        """Count purchase orders by status."""
        return self.session.query(PurchaseOrderModel).filter(
            PurchaseOrderModel.status == status.value
        ).count()

    async def get_next_order_number(self) -> str:
        """Generate the next purchase order number."""
        # This is a simple implementation. In production, you might want to use
        # the IDManager entity or a more sophisticated sequence generator
        from ...domain.entities.id_manager import IDManager
        
        # Get the last order number
        last_po = self.session.query(PurchaseOrderModel).order_by(
            PurchaseOrderModel.order_number.desc()
        ).first()
        
        if last_po and last_po.order_number.startswith("PUR-"):
            try:
                # Extract the numeric part and increment
                last_num = int(last_po.order_number.split("-")[1])
                new_num = last_num + 1
                return f"PUR-{new_num:06d}"
            except (ValueError, IndexError):
                pass
        
        # Default to PUR-000001 if no previous orders or parsing fails
        return "PUR-000001"

    def _model_to_entity(self, model: PurchaseOrderModel) -> PurchaseOrder:
        """Convert a database model to a domain entity."""
        return PurchaseOrder(
            order_number=model.order_number,
            vendor_id=model.vendor_id,
            order_date=model.order_date,
            expected_delivery_date=model.expected_delivery_date,
            status=PurchaseOrderStatus(model.status),
            total_amount=Decimal(str(model.total_amount)),
            total_tax_amount=Decimal(str(model.total_tax_amount)),
            total_discount=Decimal(str(model.total_discount)),
            grand_total=Decimal(str(model.grand_total)),
            reference_number=model.reference_number,
            invoice_number=model.invoice_number,
            notes=model.notes,
            purchase_order_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active,
        )