"""Purchase Transaction Item Repository Implementation

This module provides the SQLAlchemy implementation of the IPurchaseTransactionItemRepository interface.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem
from src.domain.repositories.purchase_transaction_item_repository import IPurchaseTransactionItemRepository
from src.infrastructure.database.models import PurchaseTransactionItemModel


class SQLAlchemyPurchaseTransactionItemRepository(IPurchaseTransactionItemRepository):
    """SQLAlchemy implementation of the purchase transaction item repository."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
    
    async def create(self, item: PurchaseTransactionItem) -> PurchaseTransactionItem:
        """Create a new purchase transaction item."""
        model = self._entity_to_model(item)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def bulk_create(self, items: List[PurchaseTransactionItem]) -> List[PurchaseTransactionItem]:
        """Create multiple purchase transaction items atomically."""
        models = [self._entity_to_model(item) for item in items]
        self.session.add_all(models)
        self.session.commit()
        
        # Refresh all models to get generated IDs
        for model in models:
            self.session.refresh(model)
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_id(self, item_id: UUID) -> Optional[PurchaseTransactionItem]:
        """Retrieve a purchase transaction item by its ID."""
        model = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.id == item_id,
            PurchaseTransactionItemModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_transaction_id(
        self,
        transaction_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseTransactionItem]:
        """Get all items for a specific purchase transaction."""
        models = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.transaction_id == transaction_id,
            PurchaseTransactionItemModel.is_active == True
        ).order_by(
            PurchaseTransactionItemModel.created_at.asc()
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, item: PurchaseTransactionItem) -> PurchaseTransactionItem:
        """Update an existing purchase transaction item."""
        model = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.id == item.id
        ).first()
        
        if not model:
            raise ValueError(f"Purchase transaction item with id {item.id} not found")
        
        # Update model fields
        model.transaction_id = item.transaction_id
        model.inventory_item_id = item.inventory_item_id
        model.warehouse_id = item.warehouse_id
        model.quantity = item.quantity
        model.unit_price = float(item.unit_price)
        model.discount = float(item.discount)
        model.tax_amount = float(item.tax_amount)
        model.total_price = float(item.total_price)
        model.serial_number = item.serial_number
        model.remarks = item.remarks
        model.warranty_period_type = item.warranty_period_type
        model.warranty_period = item.warranty_period
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, item_id: UUID) -> bool:
        """Soft delete a purchase transaction item."""
        model = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.id == item_id
        ).first()
        
        if not model:
            return False
        
        model.is_active = False
        self.session.commit()
        return True
    
    async def count_by_transaction_id(self, transaction_id: UUID) -> int:
        """Count items for a specific purchase transaction."""
        return self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.transaction_id == transaction_id,
            PurchaseTransactionItemModel.is_active == True
        ).count()
    
    async def get_by_inventory_item_id(
        self,
        inventory_item_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseTransactionItem]:
        """Get all purchase transaction items for a specific inventory item."""
        models = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.inventory_item_id == inventory_item_id,
            PurchaseTransactionItemModel.is_active == True
        ).order_by(
            PurchaseTransactionItemModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_warehouse_id(
        self,
        warehouse_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseTransactionItem]:
        """Get all purchase transaction items for a specific warehouse."""
        models = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.warehouse_id == warehouse_id,
            PurchaseTransactionItemModel.is_active == True
        ).order_by(
            PurchaseTransactionItemModel.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_serial_number(self, serial_number: str) -> Optional[PurchaseTransactionItem]:
        """Find a purchase transaction item by serial number."""
        # Search in JSON array using PostgreSQL JSON operators
        model = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.serial_number.op('@>')([serial_number]),
            PurchaseTransactionItemModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def check_serial_number_exists(self, serial_number: str) -> bool:
        """Check if a serial number already exists in any purchase transaction item."""
        exists = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.serial_number.op('@>')([serial_number]),
            PurchaseTransactionItemModel.is_active == True
        ).first() is not None
        
        return exists
    
    async def validate_serial_numbers_unique(self, serial_numbers: List[str]) -> bool:
        """Validate that all provided serial numbers are unique across the system."""
        for serial_number in serial_numbers:
            if await self.check_serial_number_exists(serial_number):
                return False
        return True
    
    async def get_transaction_item_summary(self, transaction_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for all items in a transaction."""
        query = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.transaction_id == transaction_id,
            PurchaseTransactionItemModel.is_active == True
        )
        
        # Get aggregated data
        result = query.with_entities(
            func.count(PurchaseTransactionItemModel.id).label('total_items'),
            func.sum(PurchaseTransactionItemModel.quantity).label('total_quantity'),
            func.sum(PurchaseTransactionItemModel.total_price).label('total_amount'),
            func.sum(PurchaseTransactionItemModel.discount).label('total_discount'),
            func.sum(PurchaseTransactionItemModel.tax_amount).label('total_tax'),
            func.avg(PurchaseTransactionItemModel.unit_price).label('avg_unit_price')
        ).first()
        
        summary = {
            'total_items': result.total_items or 0,
            'total_quantity': result.total_quantity or 0,
            'total_amount': float(result.total_amount) if result.total_amount else 0.0,
            'total_discount': float(result.total_discount) if result.total_discount else 0.0,
            'total_tax': float(result.total_tax) if result.total_tax else 0.0,
            'average_unit_price': float(result.avg_unit_price) if result.avg_unit_price else 0.0,
            'items_with_warranty': 0,
            'items_with_serial_numbers': 0
        }
        
        # Count items with warranty
        warranty_count = query.filter(
            PurchaseTransactionItemModel.warranty_period_type.isnot(None)
        ).count()
        summary['items_with_warranty'] = warranty_count
        
        # Count items with serial numbers
        serial_count = query.filter(
            func.jsonb_array_length(PurchaseTransactionItemModel.serial_number) > 0
        ).count()
        summary['items_with_serial_numbers'] = serial_count
        
        return summary
    
    async def update_pricing(
        self,
        item_id: UUID,
        unit_price: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None
    ) -> PurchaseTransactionItem:
        """Update pricing information for an item."""
        model = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.id == item_id
        ).first()
        
        if not model:
            raise ValueError(f"Purchase transaction item with id {item_id} not found")
        
        # Update pricing fields if provided
        if unit_price is not None:
            model.unit_price = float(unit_price)
        
        if discount is not None:
            model.discount = float(discount)
        
        if tax_amount is not None:
            model.tax_amount = float(tax_amount)
        
        # Recalculate total price
        subtotal = model.unit_price * model.quantity
        model.total_price = subtotal - model.discount + model.tax_amount
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_items_with_warranty(
        self,
        warranty_expiring_before: Optional[str] = None
    ) -> List[PurchaseTransactionItem]:
        """Get all items that have warranty information."""
        query = self.session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.warranty_period_type.isnot(None),
            PurchaseTransactionItemModel.warranty_period.isnot(None),
            PurchaseTransactionItemModel.is_active == True
        )
        
        # TODO: Add warranty expiration calculation if warranty_expiring_before is provided
        # This would require joining with the transaction table to get the transaction date
        # and calculating the warranty expiration date based on warranty_period and warranty_period_type
        
        models = query.order_by(PurchaseTransactionItemModel.created_at.desc()).all()
        return [self._model_to_entity(model) for model in models]
    
    def _entity_to_model(self, entity: PurchaseTransactionItem) -> PurchaseTransactionItemModel:
        """Convert domain entity to database model."""
        return PurchaseTransactionItemModel(
            id=entity.id,
            transaction_id=entity.transaction_id,
            inventory_item_id=entity.inventory_item_id,
            warehouse_id=entity.warehouse_id,
            quantity=entity.quantity,
            unit_price=float(entity.unit_price),
            discount=float(entity.discount),
            tax_amount=float(entity.tax_amount),
            total_price=float(entity.total_price),
            serial_number=entity.serial_number,
            remarks=entity.remarks,
            warranty_period_type=entity.warranty_period_type,
            warranty_period=entity.warranty_period,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            is_active=entity.is_active
        )
    
    def _model_to_entity(self, model: PurchaseTransactionItemModel) -> PurchaseTransactionItem:
        """Convert database model to domain entity."""
        if not model:
            return None
        
        return PurchaseTransactionItem(
            id=model.id,
            transaction_id=model.transaction_id,
            inventory_item_id=model.inventory_item_id,
            warehouse_id=model.warehouse_id,
            quantity=model.quantity,
            unit_price=Decimal(str(model.unit_price)),
            discount=Decimal(str(model.discount)),
            tax_amount=Decimal(str(model.tax_amount)),
            total_price=Decimal(str(model.total_price)),
            serial_number=model.serial_number or [],
            remarks=model.remarks,
            warranty_period_type=model.warranty_period_type,
            warranty_period=model.warranty_period,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active
        )