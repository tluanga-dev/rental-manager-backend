"""Sales Return Item Repository Implementation

This module provides the SQLAlchemy implementation of the ISalesReturnItemRepository interface.
"""

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domain.entities.sales import SalesReturnItem
from src.domain.repositories.sales_return_item_repository import ISalesReturnItemRepository
from src.infrastructure.database.models import SalesReturnItemModel


class SQLAlchemySalesReturnItemRepository(ISalesReturnItemRepository):
    """SQLAlchemy implementation of the sales return item repository."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
    
    async def create(self, item: SalesReturnItem) -> SalesReturnItem:
        """Create a new sales return item."""
        model = self._entity_to_model(item)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def create_batch(self, items: List[SalesReturnItem]) -> List[SalesReturnItem]:
        """Create multiple sales return items in a batch."""
        models = [self._entity_to_model(item) for item in items]
        self.session.add_all(models)
        self.session.commit()
        
        # Refresh all models
        for model in models:
            self.session.refresh(model)
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_id(self, item_id: str) -> Optional[SalesReturnItem]:
        """Retrieve a sales return item by its ID."""
        model = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.id == item_id,
            SalesReturnItemModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_return(self, sales_return_id: str) -> List[SalesReturnItem]:
        """Get all items for a specific sales return."""
        models = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.sales_return_id == sales_return_id,
            SalesReturnItemModel.is_active == True
        ).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_sales_item(self, sales_item_id: str) -> List[SalesReturnItem]:
        """Get all return items for a specific sales transaction item."""
        models = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.sales_item_id == sales_item_id,
            SalesReturnItemModel.is_active == True
        ).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, item: SalesReturnItem) -> SalesReturnItem:
        """Update an existing sales return item."""
        model = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.id == item.id
        ).first()
        
        if not model:
            raise ValueError(f"Sales return item with id {item.id} not found")
        
        # Update model fields
        model.sales_return_id = item.sales_return_id
        model.sales_item_id = item.sales_item_id
        model.quantity = item.quantity
        model.condition = item.condition
        model.serial_numbers = item.serial_numbers
        model.updated_at = item.updated_at
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, item_id: str) -> bool:
        """Delete a sales return item."""
        model = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.id == item_id
        ).first()
        
        if model:
            model.is_active = False
            self.session.commit()
            return True
        return False
    
    async def delete_by_return(self, sales_return_id: str) -> int:
        """Delete all items for a specific sales return."""
        result = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.sales_return_id == sales_return_id,
            SalesReturnItemModel.is_active == True
        ).update({'is_active': False})
        
        self.session.commit()
        return result
    
    async def get_total_returned_quantity(self, sales_item_id: str) -> int:
        """Get the total quantity returned for a sales transaction item."""
        result = self.session.query(
            func.sum(SalesReturnItemModel.quantity)
        ).join(
            SalesReturnItemModel.sales_return
        ).filter(
            SalesReturnItemModel.sales_item_id == sales_item_id,
            SalesReturnItemModel.is_active == True,
            # Only count approved returns
            SalesReturnItemModel.sales_return.has(approved_by_id__isnot=None)
        ).scalar()
        
        return result or 0
    
    async def get_by_serial_number(self, serial_number: str) -> Optional[SalesReturnItem]:
        """Find a sales return item by serial number."""
        # Using PostgreSQL's array contains operator
        model = self.session.query(SalesReturnItemModel).filter(
            SalesReturnItemModel.serial_numbers.contains([serial_number]),
            SalesReturnItemModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_resellable_items(self, warehouse_id: Optional[str] = None) -> List[SalesReturnItem]:
        """Get all return items that are in resellable condition."""
        resellable_conditions = ['new', 'unopened', 'like new', 'excellent', 'good']
        
        query = self.session.query(SalesReturnItemModel).join(
            SalesReturnItemModel.sales_return
        ).filter(
            SalesReturnItemModel.condition.in_(resellable_conditions),
            SalesReturnItemModel.is_active == True,
            # Only approved returns
            SalesReturnItemModel.sales_return.has(approved_by_id__isnot=None)
        )
        
        if warehouse_id:
            # Join with sales item to filter by warehouse
            query = query.join(
                SalesReturnItemModel.sales_item
            ).filter(
                SalesReturnItemModel.sales_item.has(warehouse_id=warehouse_id)
            )
        
        models = query.all()
        return [self._model_to_entity(model) for model in models]
    
    def _entity_to_model(self, entity: SalesReturnItem) -> SalesReturnItemModel:
        """Convert domain entity to database model."""
        return SalesReturnItemModel(
            id=entity.id,
            sales_return_id=entity.sales_return_id,
            sales_item_id=entity.sales_item_id,
            quantity=entity.quantity,
            condition=entity.condition,
            serial_numbers=entity.serial_numbers,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            is_active=entity.is_active
        )
    
    def _model_to_entity(self, model: SalesReturnItemModel) -> SalesReturnItem:
        """Convert database model to domain entity."""
        if not model:
            return None
        
        return SalesReturnItem(
            id=model.id,
            sales_return_id=model.sales_return_id,
            sales_item_id=model.sales_item_id,
            quantity=model.quantity,
            condition=model.condition,
            serial_numbers=model.serial_numbers or [],
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active
        )