"""Purchase Transaction Repository Implementation

This module provides the SQLAlchemy implementation of the IPurchaseTransactionRepository interface.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.repositories.purchase_transaction_repository import IPurchaseTransactionRepository
from src.infrastructure.database.models import (
    PurchaseTransactionModel
)


class SQLAlchemyPurchaseTransactionRepository(IPurchaseTransactionRepository):
    """SQLAlchemy implementation of the purchase transaction repository."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
    
    async def create(self, purchase_transaction: PurchaseTransaction) -> PurchaseTransaction:
        """Create a new purchase transaction."""
        model = self._entity_to_model(purchase_transaction)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, transaction_id: str) -> Optional[PurchaseTransaction]:
        """Retrieve a purchase transaction by its ID."""
        model = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.id == transaction_id,
            PurchaseTransactionModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[PurchaseTransaction]:
        """Retrieve a purchase transaction by its transaction ID."""
        model = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.transaction_id == transaction_id,
            PurchaseTransactionModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def update(self, purchase_transaction: PurchaseTransaction) -> PurchaseTransaction:
        """Update an existing purchase transaction."""
        model = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.id == purchase_transaction.id
        ).first()
        
        if not model:
            raise ValueError(f"Purchase transaction with id {purchase_transaction.id} not found")
        
        # Update model fields
        model.transaction_id = purchase_transaction.transaction_id
        model.transaction_date = purchase_transaction.transaction_date
        model.vendor_id = purchase_transaction.vendor_id
        model.total_amount = float(purchase_transaction.total_amount)
        model.grand_total = float(purchase_transaction.grand_total)
        model.purchase_order_number = purchase_transaction.purchase_order_number
        model.remarks = purchase_transaction.remarks
        model.updated_at = datetime.now()
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, transaction_id: str) -> bool:
        """Soft delete a purchase transaction."""
        model = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.id == transaction_id
        ).first()
        
        if not model:
            return False
        
        model.is_active = False
        self.session.commit()
        return True
    
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = True
    ) -> List[PurchaseTransaction]:
        """List purchase transactions with optional filtering and pagination."""
        query = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.is_active == True
        )
        
        # Apply filters
        if filters:
            if 'vendor_id' in filters and filters['vendor_id']:
                query = query.filter(PurchaseTransactionModel.vendor_id == filters['vendor_id'])
            
            if 'date_from' in filters and filters['date_from']:
                query = query.filter(PurchaseTransactionModel.transaction_date >= filters['date_from'])
            
            if 'date_to' in filters and filters['date_to']:
                query = query.filter(PurchaseTransactionModel.transaction_date <= filters['date_to'])
            
            if 'purchase_order_number' in filters and filters['purchase_order_number']:
                query = query.filter(
                    PurchaseTransactionModel.purchase_order_number.ilike(f"%{filters['purchase_order_number']}%")
                )
        
        # Apply sorting
        if sort_by:
            column = getattr(PurchaseTransactionModel, sort_by, None)
            if column:
                if sort_desc:
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column)
        else:
            query = query.order_by(PurchaseTransactionModel.transaction_date.desc())
        
        query = query.offset(skip).limit(limit)
        models = query.all()
        return [self._model_to_entity(model) for model in models]
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count purchase transactions with optional filtering."""
        query = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.is_active == True
        )
        
        # Apply filters
        if filters:
            if 'vendor_id' in filters and filters['vendor_id']:
                query = query.filter(PurchaseTransactionModel.vendor_id == filters['vendor_id'])
            
            if 'date_from' in filters and filters['date_from']:
                query = query.filter(PurchaseTransactionModel.transaction_date >= filters['date_from'])
            
            if 'date_to' in filters and filters['date_to']:
                query = query.filter(PurchaseTransactionModel.transaction_date <= filters['date_to'])
            
            if 'purchase_order_number' in filters and filters['purchase_order_number']:
                query = query.filter(
                    PurchaseTransactionModel.purchase_order_number.ilike(f"%{filters['purchase_order_number']}%")
                )
        
        return query.count()
    
    async def get_by_vendor(
        self,
        vendor_id: str,
        skip: int = 0,
        limit: int = 100,
        include_cancelled: bool = False
    ) -> List[PurchaseTransaction]:
        """Get all purchase transactions for a specific vendor."""
        query = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.vendor_id == vendor_id,
            PurchaseTransactionModel.is_active == True
        )
        
        query = query.order_by(PurchaseTransactionModel.transaction_date.desc())
        query = query.offset(skip).limit(limit)
        
        models = query.all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_purchase_order_number(
        self, 
        purchase_order_number: str
    ) -> Optional[PurchaseTransaction]:
        """Get purchase transaction by purchase order number."""
        model = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.purchase_order_number == purchase_order_number,
            PurchaseTransactionModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_purchase_summary(
        self,
        start_date: date,
        end_date: date,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get purchase summary statistics for a date range."""
        base_query = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.transaction_date >= start_date,
            PurchaseTransactionModel.transaction_date <= end_date,
            PurchaseTransactionModel.is_active == True
        )
        
        summary = {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_transactions': base_query.count(),
            'total_amount': 0.0,
            'grand_total': 0.0,
            'average_amount': 0.0,
        }
        
        # Calculate totals
        totals = base_query.with_entities(
            func.sum(PurchaseTransactionModel.total_amount).label('total_amount'),
            func.sum(PurchaseTransactionModel.grand_total).label('grand_total'),
            func.avg(PurchaseTransactionModel.grand_total).label('avg_amount')
        ).first()
        
        if totals:
            summary['total_amount'] = float(totals.total_amount) if totals.total_amount else 0.0
            summary['grand_total'] = float(totals.grand_total) if totals.grand_total else 0.0
            summary['average_amount'] = float(totals.avg_amount) if totals.avg_amount else 0.0
        
        return summary
    
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PurchaseTransaction]:
        """Search purchase transactions by text query."""
        search_query = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.is_active == True
        )
        
        # Build OR conditions for search
        conditions = [
            PurchaseTransactionModel.transaction_id.ilike(f'%{query}%'),
            PurchaseTransactionModel.purchase_order_number.ilike(f'%{query}%'),
            PurchaseTransactionModel.remarks.ilike(f'%{query}%')
        ]
        
        search_query = search_query.filter(or_(*conditions))
        
        # Apply additional filters
        if filters:
            if 'vendor_id' in filters and filters['vendor_id']:
                search_query = search_query.filter(PurchaseTransactionModel.vendor_id == filters['vendor_id'])
        
        models = search_query.limit(100).all()
        return [self._model_to_entity(model) for model in models]
    
    async def update_totals(
        self,
        transaction_id: str,
        total_amount: Decimal,
        grand_total: Decimal
    ) -> PurchaseTransaction:
        """Update the totals of a purchase transaction."""
        model = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.id == transaction_id
        ).first()
        
        if not model:
            raise ValueError(f"Purchase transaction with id {transaction_id} not found")
        
        model.total_amount = float(total_amount)
        model.grand_total = float(grand_total)
        model.updated_at = datetime.now()
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def exists_by_transaction_id(self, transaction_id: str) -> bool:
        """Check if a purchase transaction exists with the given transaction ID."""
        return self.session.query(
            PurchaseTransactionModel
        ).filter(
            PurchaseTransactionModel.transaction_id == transaction_id,
            PurchaseTransactionModel.is_active == True
        ).first() is not None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get general purchase transaction statistics."""
        total_query = self.session.query(PurchaseTransactionModel).filter(
            PurchaseTransactionModel.is_active == True
        )
        
        stats = {}
        
        # Total amount
        total_amount = total_query.with_entities(
            func.sum(PurchaseTransactionModel.grand_total)
        ).scalar()
        
        stats['total_amount'] = float(total_amount) if total_amount else 0.0
        stats['total_transactions'] = total_query.count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = date.today().replace(day=1)  # Start of current month
        recent_query = total_query.filter(
            PurchaseTransactionModel.transaction_date >= thirty_days_ago
        )
        
        recent_amount = recent_query.with_entities(
            func.sum(PurchaseTransactionModel.grand_total)
        ).scalar()
        
        stats['recent_amount'] = float(recent_amount) if recent_amount else 0.0
        stats['recent_transactions'] = recent_query.count()
        
        return stats
    
    def _entity_to_model(self, entity: PurchaseTransaction) -> PurchaseTransactionModel:
        """Convert domain entity to database model."""
        return PurchaseTransactionModel(
            id=entity.id,
            transaction_id=entity.transaction_id,
            transaction_date=entity.transaction_date,
            vendor_id=entity.vendor_id,
            total_amount=float(entity.total_amount),
            grand_total=float(entity.grand_total),
            purchase_order_number=entity.purchase_order_number,
            remarks=entity.remarks,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            is_active=entity.is_active
        )
    
    def _model_to_entity(self, model: PurchaseTransactionModel) -> PurchaseTransaction:
        """Convert database model to domain entity."""
        if not model:
            return None
        
        return PurchaseTransaction(
            transaction_id=model.transaction_id,
            transaction_date=model.transaction_date,
            vendor_id=model.vendor_id,
            total_amount=Decimal(str(model.total_amount)),
            grand_total=Decimal(str(model.grand_total)),
            purchase_order_number=model.purchase_order_number,
            remarks=model.remarks,
            entity_id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active
        )