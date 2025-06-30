"""Sales Transaction Item Repository Implementation

This module provides the SQLAlchemy implementation of the ISalesTransactionItemRepository interface.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import ARRAY

from src.domain.entities.sales import SalesTransactionItem
from src.domain.repositories.sales_transaction_item_repository import ISalesTransactionItemRepository
from src.infrastructure.database.models import SalesTransactionItemModel


class SQLAlchemySalesTransactionItemRepository(ISalesTransactionItemRepository):
    """SQLAlchemy implementation of the sales transaction item repository."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
    
    async def create(self, item: SalesTransactionItem) -> SalesTransactionItem:
        """Create a new sales transaction item."""
        model = self._entity_to_model(item)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def create_batch(self, items: List[SalesTransactionItem]) -> List[SalesTransactionItem]:
        """Create multiple sales transaction items in a batch."""
        models = [self._entity_to_model(item) for item in items]
        self.session.add_all(models)
        self.session.commit()
        
        # Refresh all models
        for model in models:
            self.session.refresh(model)
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_id(self, item_id: UUID) -> Optional[SalesTransactionItem]:
        """Retrieve a sales transaction item by its ID."""
        model = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.id == item_id,
            SalesTransactionItemModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_transaction(self, transaction_id: UUID) -> List[SalesTransactionItem]:
        """Get all items for a specific sales transaction."""
        models = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.transaction_id == transaction_id,
            SalesTransactionItemModel.is_active == True
        ).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, item: SalesTransactionItem) -> SalesTransactionItem:
        """Update an existing sales transaction item."""
        model = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.id == item.id
        ).first()
        
        if not model:
            raise ValueError(f"Sales transaction item with id {item.id} not found")
        
        # Update model fields
        model.transaction_id = item.transaction_id
        model.inventory_item_master_id = item.inventory_item_master_id
        model.warehouse_id = item.warehouse_id
        model.quantity = item.quantity
        model.unit_price = float(item.unit_price)
        model.cost_price = float(item.cost_price)
        model.discount_percentage = float(item.discount_percentage)
        model.discount_amount = float(item.discount_amount)
        model.tax_rate = float(item.tax_rate)
        model.tax_amount = float(item.tax_amount)
        model.subtotal = float(item.subtotal)
        model.total = float(item.total)
        model.serial_numbers = item.serial_numbers
        model.notes = item.notes
        model.updated_at = item.updated_at
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def update_batch(self, items: List[SalesTransactionItem]) -> List[SalesTransactionItem]:
        """Update multiple sales transaction items in a batch."""
        updated_models = []
        
        for item in items:
            model = self.session.query(SalesTransactionItemModel).filter(
                SalesTransactionItemModel.id == item.id
            ).first()
            
            if model:
                # Update model fields
                model.quantity = item.quantity
                model.unit_price = float(item.unit_price)
                model.cost_price = float(item.cost_price)
                model.discount_percentage = float(item.discount_percentage)
                model.discount_amount = float(item.discount_amount)
                model.tax_rate = float(item.tax_rate)
                model.tax_amount = float(item.tax_amount)
                model.subtotal = float(item.subtotal)
                model.total = float(item.total)
                model.serial_numbers = item.serial_numbers
                model.notes = item.notes
                model.updated_at = item.updated_at
                updated_models.append(model)
        
        self.session.commit()
        
        # Refresh all models
        for model in updated_models:
            self.session.refresh(model)
        
        return [self._model_to_entity(model) for model in updated_models]
    
    async def delete(self, item_id: UUID) -> bool:
        """Delete a sales transaction item."""
        model = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.id == item_id
        ).first()
        
        if model:
            model.is_active = False
            self.session.commit()
            return True
        return False
    
    async def delete_by_transaction(self, transaction_id: UUID) -> int:
        """Delete all items for a specific sales transaction."""
        result = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.transaction_id == transaction_id,
            SalesTransactionItemModel.is_active == True
        ).update({'is_active': False})
        
        self.session.commit()
        return result
    
    async def get_by_inventory_item(
        self,
        inventory_item_master_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesTransactionItem]:
        """Get all sales transaction items for a specific inventory item."""
        models = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.inventory_item_master_id == inventory_item_master_id,
            SalesTransactionItemModel.is_active == True
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_warehouse(
        self,
        warehouse_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesTransactionItem]:
        """Get all sales transaction items from a specific warehouse."""
        models = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.warehouse_id == warehouse_id,
            SalesTransactionItemModel.is_active == True
        ).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def update_price(
        self,
        item_id: UUID,
        unit_price: Decimal
    ) -> SalesTransactionItem:
        """Update the unit price of a sales transaction item."""
        model = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.id == item_id
        ).first()
        
        if not model:
            raise ValueError(f"Sales transaction item with id {item_id} not found")
        
        model.unit_price = float(unit_price)
        
        # Recalculate totals
        base_amount = model.unit_price * model.quantity
        
        # Apply discount
        if model.discount_percentage > 0:
            model.discount_amount = base_amount * (model.discount_percentage / 100)
        
        model.subtotal = base_amount - model.discount_amount
        
        # Calculate tax
        if model.tax_rate > 0:
            model.tax_amount = model.subtotal * (model.tax_rate / 100)
        else:
            model.tax_amount = 0
        
        # Calculate total
        model.total = model.subtotal + model.tax_amount
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_total_quantity_sold(
        self,
        inventory_item_master_id: UUID,
        warehouse_id: Optional[UUID] = None
    ) -> int:
        """Get the total quantity sold for an inventory item."""
        query = self.session.query(
            func.sum(SalesTransactionItemModel.quantity)
        ).filter(
            SalesTransactionItemModel.inventory_item_master_id == inventory_item_master_id,
            SalesTransactionItemModel.is_active == True
        )
        
        if warehouse_id:
            query = query.filter(SalesTransactionItemModel.warehouse_id == warehouse_id)
        
        result = query.scalar()
        return result or 0
    
    async def get_sales_by_serial_number(self, serial_number: str) -> Optional[SalesTransactionItem]:
        """Find a sales transaction item by serial number."""
        # Using PostgreSQL's array contains operator
        model = self.session.query(SalesTransactionItemModel).filter(
            SalesTransactionItemModel.serial_numbers.contains([serial_number]),
            SalesTransactionItemModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def calculate_transaction_totals(self, transaction_id: UUID) -> Dict[str, Decimal]:
        """Calculate totals for all items in a transaction."""
        result = self.session.query(
            func.sum(SalesTransactionItemModel.subtotal + SalesTransactionItemModel.discount_amount).label('subtotal'),
            func.sum(SalesTransactionItemModel.tax_amount).label('tax_total'),
            func.sum(SalesTransactionItemModel.discount_amount).label('discount_total'),
            func.sum(SalesTransactionItemModel.total).label('grand_total')
        ).filter(
            SalesTransactionItemModel.transaction_id == transaction_id,
            SalesTransactionItemModel.is_active == True
        ).first()
        
        return {
            'subtotal': Decimal(str(result.subtotal or 0)),
            'tax_total': Decimal(str(result.tax_total or 0)),
            'discount_total': Decimal(str(result.discount_total or 0)),
            'grand_total': Decimal(str(result.grand_total or 0))
        }
    
    def _entity_to_model(self, entity: SalesTransactionItem) -> SalesTransactionItemModel:
        """Convert domain entity to database model."""
        return SalesTransactionItemModel(
            id=entity.id,
            transaction_id=entity.transaction_id,
            inventory_item_master_id=entity.inventory_item_master_id,
            warehouse_id=entity.warehouse_id,
            quantity=entity.quantity,
            unit_price=float(entity.unit_price),
            cost_price=float(entity.cost_price),
            discount_percentage=float(entity.discount_percentage),
            discount_amount=float(entity.discount_amount),
            tax_rate=float(entity.tax_rate),
            tax_amount=float(entity.tax_amount),
            subtotal=float(entity.subtotal),
            total=float(entity.total),
            serial_numbers=entity.serial_numbers,
            notes=entity.notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            is_active=entity.is_active
        )
    
    def _model_to_entity(self, model: SalesTransactionItemModel) -> SalesTransactionItem:
        """Convert database model to domain entity."""
        if not model:
            return None
        
        return SalesTransactionItem(
            id=model.id,
            transaction_id=model.transaction_id,
            inventory_item_master_id=model.inventory_item_master_id,
            warehouse_id=model.warehouse_id,
            quantity=model.quantity,
            unit_price=Decimal(str(model.unit_price)),
            cost_price=Decimal(str(model.cost_price)),
            discount_percentage=Decimal(str(model.discount_percentage)),
            discount_amount=Decimal(str(model.discount_amount)),
            tax_rate=Decimal(str(model.tax_rate)),
            tax_amount=Decimal(str(model.tax_amount)),
            subtotal=Decimal(str(model.subtotal)),
            total=Decimal(str(model.total)),
            serial_numbers=model.serial_numbers or [],
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active
        )