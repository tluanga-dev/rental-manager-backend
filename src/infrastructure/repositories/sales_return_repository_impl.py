"""Sales Return Repository Implementation

This module provides the SQLAlchemy implementation of the ISalesReturnRepository interface.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.domain.entities.sales import SalesReturn
from src.domain.repositories.sales_return_repository import ISalesReturnRepository
from src.infrastructure.database.models import SalesReturnModel


class SQLAlchemySalesReturnRepository(ISalesReturnRepository):
    """SQLAlchemy implementation of the sales return repository."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
    
    async def create(self, sales_return: SalesReturn) -> SalesReturn:
        """Create a new sales return."""
        model = self._entity_to_model(sales_return)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, return_id: UUID) -> Optional[SalesReturn]:
        """Retrieve a sales return by its ID."""
        model = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.id == return_id,
            SalesReturnModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_return_id(self, return_id: str) -> Optional[SalesReturn]:
        """Retrieve a sales return by its return ID (e.g., SRT-001)."""
        model = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.return_id == return_id,
            SalesReturnModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_transaction(self, sales_transaction_id: UUID) -> List[SalesReturn]:
        """Get all returns for a specific sales transaction."""
        models = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.sales_transaction_id == sales_transaction_id,
            SalesReturnModel.is_active == True
        ).order_by(SalesReturnModel.return_date.desc()).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def update(self, sales_return: SalesReturn) -> SalesReturn:
        """Update an existing sales return."""
        model = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.id == sales_return.id
        ).first()
        
        if not model:
            raise ValueError(f"Sales return with id {sales_return.id} not found")
        
        # Update model fields
        model.return_id = sales_return.return_id
        model.sales_transaction_id = sales_return.sales_transaction_id
        model.return_date = sales_return.return_date
        model.reason = sales_return.reason
        model.approved_by_id = sales_return.approved_by_id
        model.refund_amount = float(sales_return.refund_amount)
        model.restocking_fee = float(sales_return.restocking_fee)
        model.updated_at = sales_return.updated_at
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, return_id: UUID) -> bool:
        """Soft delete a sales return."""
        model = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.id == return_id
        ).first()
        
        if model:
            model.is_active = False
            self.session.commit()
            return True
        return False
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = True
    ) -> List[SalesReturn]:
        """List sales returns with optional filtering and pagination."""
        query = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.is_active == True
        )
        
        # Apply filters
        if filters:
            if 'start_date' in filters:
                query = query.filter(SalesReturnModel.return_date >= filters['start_date'])
            if 'end_date' in filters:
                query = query.filter(SalesReturnModel.return_date <= filters['end_date'])
            if 'approved_by_id' in filters:
                query = query.filter(SalesReturnModel.approved_by_id == filters['approved_by_id'])
            if 'sales_transaction_id' in filters:
                query = query.filter(SalesReturnModel.sales_transaction_id == filters['sales_transaction_id'])
        
        # Apply sorting
        if sort_by:
            sort_column = getattr(SalesReturnModel, sort_by, SalesReturnModel.return_date)
            query = query.order_by(sort_column.desc() if sort_desc else sort_column.asc())
        else:
            query = query.order_by(SalesReturnModel.return_date.desc())
        
        # Apply pagination
        models = query.offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count sales returns with optional filtering."""
        query = self.session.query(func.count(SalesReturnModel.id)).filter(
            SalesReturnModel.is_active == True
        )
        
        # Apply same filters as list method
        if filters:
            if 'start_date' in filters:
                query = query.filter(SalesReturnModel.return_date >= filters['start_date'])
            if 'end_date' in filters:
                query = query.filter(SalesReturnModel.return_date <= filters['end_date'])
            if 'approved_by_id' in filters:
                query = query.filter(SalesReturnModel.approved_by_id == filters['approved_by_id'])
            if 'sales_transaction_id' in filters:
                query = query.filter(SalesReturnModel.sales_transaction_id == filters['sales_transaction_id'])
        
        return query.scalar()
    
    async def get_pending_approval(self) -> List[SalesReturn]:
        """Get all sales returns pending approval."""
        models = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.approved_by_id.is_(None),
            SalesReturnModel.is_active == True
        ).order_by(SalesReturnModel.return_date.asc()).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[SalesReturn]:
        """Get sales returns within a date range."""
        models = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.return_date >= start_date,
            SalesReturnModel.return_date <= end_date,
            SalesReturnModel.is_active == True
        ).order_by(SalesReturnModel.return_date.desc()).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_total_refund_amount(self, sales_transaction_id: UUID) -> Decimal:
        """Calculate the total refund amount for a sales transaction."""
        result = self.session.query(
            func.sum(SalesReturnModel.refund_amount)
        ).filter(
            SalesReturnModel.sales_transaction_id == sales_transaction_id,
            SalesReturnModel.is_active == True
        ).scalar()
        
        return Decimal(str(result or 0))
    
    async def approve(
        self,
        return_id: UUID,
        approved_by_id: UUID
    ) -> SalesReturn:
        """Approve a sales return."""
        model = self.session.query(SalesReturnModel).filter(
            SalesReturnModel.id == return_id
        ).first()
        
        if not model:
            raise ValueError(f"Sales return with id {return_id} not found")
        
        if model.approved_by_id:
            raise ValueError("Sales return has already been approved")
        
        model.approved_by_id = approved_by_id
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def exists_by_return_id(self, return_id: str) -> bool:
        """Check if a sales return exists with the given return ID."""
        return self.session.query(
            SalesReturnModel
        ).filter(
            SalesReturnModel.return_id == return_id,
            SalesReturnModel.is_active == True
        ).first() is not None
    
    async def get_return_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get return summary statistics for a date range."""
        # Get aggregated data
        result = self.session.query(
            func.count(SalesReturnModel.id).label('total_returns'),
            func.sum(SalesReturnModel.refund_amount).label('total_refunded'),
            func.sum(SalesReturnModel.restocking_fee).label('total_restocking_fees'),
            func.avg(SalesReturnModel.refund_amount).label('average_refund')
        ).filter(
            SalesReturnModel.return_date >= start_date,
            SalesReturnModel.return_date <= end_date,
            SalesReturnModel.is_active == True
        ).first()
        
        summary = {
            'total_returns': result.total_returns or 0,
            'total_refunded': float(result.total_refunded or 0),
            'total_restocking_fees': float(result.total_restocking_fees or 0),
            'average_refund': float(result.average_refund or 0),
            'net_refunded': float((result.total_refunded or 0) - (result.total_restocking_fees or 0))
        }
        
        # Get approved vs pending breakdown
        approved_count = self.session.query(
            func.count(SalesReturnModel.id)
        ).filter(
            SalesReturnModel.return_date >= start_date,
            SalesReturnModel.return_date <= end_date,
            SalesReturnModel.approved_by_id.isnot(None),
            SalesReturnModel.is_active == True
        ).scalar()
        
        summary['approved_returns'] = approved_count or 0
        summary['pending_returns'] = summary['total_returns'] - summary['approved_returns']
        
        # Get top return reasons
        top_reasons = self.session.query(
            SalesReturnModel.reason,
            func.count(SalesReturnModel.id).label('count')
        ).filter(
            SalesReturnModel.return_date >= start_date,
            SalesReturnModel.return_date <= end_date,
            SalesReturnModel.is_active == True
        ).group_by(
            SalesReturnModel.reason
        ).order_by(
            func.count(SalesReturnModel.id).desc()
        ).limit(5).all()
        
        summary['top_return_reasons'] = [
            {'reason': reason, 'count': count}
            for reason, count in top_reasons
        ]
        
        return summary
    
    def _entity_to_model(self, entity: SalesReturn) -> SalesReturnModel:
        """Convert domain entity to database model."""
        return SalesReturnModel(
            id=entity.id,
            return_id=entity.return_id,
            sales_transaction_id=entity.sales_transaction_id,
            return_date=entity.return_date,
            reason=entity.reason,
            approved_by_id=entity.approved_by_id,
            refund_amount=float(entity.refund_amount),
            restocking_fee=float(entity.restocking_fee),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            is_active=entity.is_active
        )
    
    def _model_to_entity(self, model: SalesReturnModel) -> SalesReturn:
        """Convert database model to domain entity."""
        if not model:
            return None
        
        return SalesReturn(
            id=model.id,
            return_id=model.return_id,
            sales_transaction_id=model.sales_transaction_id,
            return_date=model.return_date,
            reason=model.reason,
            approved_by_id=model.approved_by_id,
            refund_amount=Decimal(str(model.refund_amount)),
            restocking_fee=Decimal(str(model.restocking_fee)),
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active
        )