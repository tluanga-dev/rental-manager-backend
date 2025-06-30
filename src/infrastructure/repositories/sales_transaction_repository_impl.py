"""Sales Transaction Repository Implementation

This module provides the SQLAlchemy implementation of the ISalesTransactionRepository interface.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session, joinedload

from src.domain.entities.sales import SalesTransaction
from src.domain.repositories.sales_transaction_repository import ISalesTransactionRepository
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms
from src.infrastructure.database.models import (
    SalesTransactionModel,
    SalesStatus as DBSalesStatus,
    PaymentStatus as DBPaymentStatus,
    PaymentTerms as DBPaymentTerms
)


class SQLAlchemySalesTransactionRepository(ISalesTransactionRepository):
    """SQLAlchemy implementation of the sales transaction repository."""
    
    def __init__(self, session: Session) -> None:
        """Initialize the repository with a database session."""
        self.session = session
    
    async def create(self, sales_transaction: SalesTransaction) -> SalesTransaction:
        """Create a new sales transaction."""
        model = self._entity_to_model(sales_transaction)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def get_by_id(self, transaction_id: UUID) -> Optional[SalesTransaction]:
        """Retrieve a sales transaction by its ID."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.id == transaction_id,
            SalesTransactionModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[SalesTransaction]:
        """Retrieve a sales transaction by its transaction ID."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.transaction_id == transaction_id,
            SalesTransactionModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def get_by_invoice_number(self, invoice_number: str) -> Optional[SalesTransaction]:
        """Retrieve a sales transaction by its invoice number."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.invoice_number == invoice_number,
            SalesTransactionModel.is_active == True
        ).first()
        
        return self._model_to_entity(model) if model else None
    
    async def update(self, sales_transaction: SalesTransaction) -> SalesTransaction:
        """Update an existing sales transaction."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.id == sales_transaction.id
        ).first()
        
        if not model:
            raise ValueError(f"Sales transaction with id {sales_transaction.id} not found")
        
        # Update model fields
        model.transaction_id = sales_transaction.transaction_id
        model.invoice_number = sales_transaction.invoice_number
        model.customer_id = sales_transaction.customer_id
        model.order_date = sales_transaction.order_date
        model.delivery_date = sales_transaction.delivery_date
        model.status = self._map_status_to_db(sales_transaction.status)
        model.payment_status = self._map_payment_status_to_db(sales_transaction.payment_status)
        model.payment_terms = self._map_payment_terms_to_db(sales_transaction.payment_terms)
        model.payment_due_date = sales_transaction.payment_due_date
        model.subtotal = float(sales_transaction.subtotal)
        model.discount_amount = float(sales_transaction.discount_amount)
        model.tax_amount = float(sales_transaction.tax_amount)
        model.shipping_amount = float(sales_transaction.shipping_amount)
        model.grand_total = float(sales_transaction.grand_total)
        model.amount_paid = float(sales_transaction.amount_paid)
        model.shipping_address = sales_transaction.shipping_address
        model.billing_address = sales_transaction.billing_address
        model.purchase_order_number = sales_transaction.purchase_order_number
        model.sales_person_id = sales_transaction.sales_person_id
        model.notes = sales_transaction.notes
        model.customer_notes = sales_transaction.customer_notes
        model.updated_at = sales_transaction.updated_at
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def delete(self, transaction_id: UUID) -> bool:
        """Soft delete a sales transaction."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.id == transaction_id
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
    ) -> List[SalesTransaction]:
        """List sales transactions with optional filtering and pagination."""
        query = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.is_active == True
        )
        
        # Apply filters
        if filters:
            if 'customer_id' in filters:
                query = query.filter(SalesTransactionModel.customer_id == filters['customer_id'])
            if 'status' in filters:
                query = query.filter(SalesTransactionModel.status == self._map_status_to_db(filters['status']))
            if 'payment_status' in filters:
                query = query.filter(SalesTransactionModel.payment_status == self._map_payment_status_to_db(filters['payment_status']))
            if 'start_date' in filters:
                query = query.filter(SalesTransactionModel.order_date >= filters['start_date'])
            if 'end_date' in filters:
                query = query.filter(SalesTransactionModel.order_date <= filters['end_date'])
        
        # Apply sorting
        if sort_by:
            sort_column = getattr(SalesTransactionModel, sort_by, SalesTransactionModel.order_date)
            query = query.order_by(sort_column.desc() if sort_desc else sort_column.asc())
        else:
            query = query.order_by(SalesTransactionModel.order_date.desc())
        
        # Apply pagination
        models = query.offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count sales transactions with optional filtering."""
        query = self.session.query(func.count(SalesTransactionModel.id)).filter(
            SalesTransactionModel.is_active == True
        )
        
        # Apply same filters as list method
        if filters:
            if 'customer_id' in filters:
                query = query.filter(SalesTransactionModel.customer_id == filters['customer_id'])
            if 'status' in filters:
                query = query.filter(SalesTransactionModel.status == self._map_status_to_db(filters['status']))
            if 'payment_status' in filters:
                query = query.filter(SalesTransactionModel.payment_status == self._map_payment_status_to_db(filters['payment_status']))
            if 'start_date' in filters:
                query = query.filter(SalesTransactionModel.order_date >= filters['start_date'])
            if 'end_date' in filters:
                query = query.filter(SalesTransactionModel.order_date <= filters['end_date'])
        
        return query.scalar()
    
    async def get_by_customer(
        self,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_cancelled: bool = False
    ) -> List[SalesTransaction]:
        """Get all sales transactions for a specific customer."""
        query = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.customer_id == customer_id,
            SalesTransactionModel.is_active == True
        )
        
        if not include_cancelled:
            query = query.filter(SalesTransactionModel.status != DBSalesStatus.CANCELLED)
        
        models = query.order_by(SalesTransactionModel.order_date.desc()).offset(skip).limit(limit).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_overdue_transactions(
        self,
        as_of_date: Optional[datetime] = None
    ) -> List[SalesTransaction]:
        """Get all overdue sales transactions."""
        check_date = as_of_date or datetime.now()
        
        models = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.payment_due_date < check_date.date(),
            SalesTransactionModel.payment_status.in_([
                DBPaymentStatus.PENDING,
                DBPaymentStatus.PARTIAL,
                DBPaymentStatus.OVERDUE
            ]),
            SalesTransactionModel.is_active == True
        ).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_pending_delivery(self) -> List[SalesTransaction]:
        """Get all sales transactions pending delivery."""
        models = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.status.in_([
                DBSalesStatus.CONFIRMED,
                DBSalesStatus.PROCESSING
            ]),
            SalesTransactionModel.is_active == True
        ).order_by(SalesTransactionModel.order_date.asc()).all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_customer_outstanding_balance(self, customer_id: UUID) -> Decimal:
        """Calculate the total outstanding balance for a customer."""
        result = self.session.query(
            func.sum(SalesTransactionModel.grand_total - SalesTransactionModel.amount_paid)
        ).filter(
            SalesTransactionModel.customer_id == customer_id,
            SalesTransactionModel.payment_status.in_([
                DBPaymentStatus.PENDING,
                DBPaymentStatus.PARTIAL,
                DBPaymentStatus.OVERDUE
            ]),
            SalesTransactionModel.is_active == True
        ).scalar()
        
        return Decimal(str(result or 0))
    
    async def get_sales_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get sales summary statistics for a date range."""
        # Base query for the date range
        base_query = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.order_date >= start_date,
            SalesTransactionModel.order_date <= end_date,
            SalesTransactionModel.status.in_([
                DBSalesStatus.CONFIRMED,
                DBSalesStatus.PROCESSING,
                DBSalesStatus.SHIPPED,
                DBSalesStatus.DELIVERED
            ]),
            SalesTransactionModel.is_active == True
        )
        
        # Calculate summary statistics
        summary = {
            'total_sales': 0,
            'total_orders': 0,
            'total_paid': 0,
            'total_outstanding': 0,
            'average_order_value': 0
        }
        
        # Get aggregated data
        result = self.session.query(
            func.sum(SalesTransactionModel.grand_total).label('total_sales'),
            func.count(SalesTransactionModel.id).label('total_orders'),
            func.sum(SalesTransactionModel.amount_paid).label('total_paid')
        ).filter(
            SalesTransactionModel.order_date >= start_date,
            SalesTransactionModel.order_date <= end_date,
            SalesTransactionModel.status.in_([
                DBSalesStatus.CONFIRMED,
                DBSalesStatus.PROCESSING,
                DBSalesStatus.SHIPPED,
                DBSalesStatus.DELIVERED
            ]),
            SalesTransactionModel.is_active == True
        ).first()
        
        if result:
            summary['total_sales'] = float(result.total_sales or 0)
            summary['total_orders'] = result.total_orders or 0
            summary['total_paid'] = float(result.total_paid or 0)
            summary['total_outstanding'] = summary['total_sales'] - summary['total_paid']
            summary['average_order_value'] = summary['total_sales'] / summary['total_orders'] if summary['total_orders'] > 0 else 0
        
        # Add grouping if requested
        if group_by == 'day':
            # Group by day
            daily_sales = self.session.query(
                func.date(SalesTransactionModel.order_date).label('date'),
                func.sum(SalesTransactionModel.grand_total).label('total'),
                func.count(SalesTransactionModel.id).label('orders')
            ).filter(
                SalesTransactionModel.order_date >= start_date,
                SalesTransactionModel.order_date <= end_date,
                SalesTransactionModel.status.in_([
                    DBSalesStatus.CONFIRMED,
                    DBSalesStatus.PROCESSING,
                    DBSalesStatus.SHIPPED,
                    DBSalesStatus.DELIVERED
                ]),
                SalesTransactionModel.is_active == True
            ).group_by(
                func.date(SalesTransactionModel.order_date)
            ).order_by(
                func.date(SalesTransactionModel.order_date)
            ).all()
            
            summary['daily_breakdown'] = [
                {
                    'date': str(row.date),
                    'total': float(row.total),
                    'orders': row.orders
                }
                for row in daily_sales
            ]
        
        return summary
    
    async def search(
        self,
        query: str,
        fields: Optional[List[str]] = None
    ) -> List[SalesTransaction]:
        """Search sales transactions by text query."""
        search_query = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.is_active == True
        )
        
        # Default fields to search
        if not fields:
            fields = ['transaction_id', 'invoice_number', 'purchase_order_number', 'notes']
        
        # Build OR conditions for search
        conditions = []
        for field in fields:
            if hasattr(SalesTransactionModel, field):
                column = getattr(SalesTransactionModel, field)
                conditions.append(column.ilike(f'%{query}%'))
        
        if conditions:
            search_query = search_query.filter(or_(*conditions))
        
        models = search_query.limit(100).all()
        return [self._model_to_entity(model) for model in models]
    
    async def update_payment_status(
        self,
        transaction_id: UUID,
        payment_status: PaymentStatus,
        amount_paid: Decimal
    ) -> SalesTransaction:
        """Update the payment status and amount for a transaction."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.id == transaction_id
        ).first()
        
        if not model:
            raise ValueError(f"Sales transaction with id {transaction_id} not found")
        
        model.payment_status = self._map_payment_status_to_db(payment_status)
        model.amount_paid = float(amount_paid)
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def update_status(
        self,
        transaction_id: UUID,
        status: SalesStatus
    ) -> SalesTransaction:
        """Update the status of a sales transaction."""
        model = self.session.query(SalesTransactionModel).filter(
            SalesTransactionModel.id == transaction_id
        ).first()
        
        if not model:
            raise ValueError(f"Sales transaction with id {transaction_id} not found")
        
        model.status = self._map_status_to_db(status)
        
        self.session.commit()
        self.session.refresh(model)
        return self._model_to_entity(model)
    
    async def exists_by_transaction_id(self, transaction_id: str) -> bool:
        """Check if a sales transaction exists with the given transaction ID."""
        return self.session.query(
            SalesTransactionModel
        ).filter(
            SalesTransactionModel.transaction_id == transaction_id,
            SalesTransactionModel.is_active == True
        ).first() is not None
    
    async def exists_by_invoice_number(self, invoice_number: str) -> bool:
        """Check if a sales transaction exists with the given invoice number."""
        return self.session.query(
            SalesTransactionModel
        ).filter(
            SalesTransactionModel.invoice_number == invoice_number,
            SalesTransactionModel.is_active == True
        ).first() is not None
    
    def _entity_to_model(self, entity: SalesTransaction) -> SalesTransactionModel:
        """Convert domain entity to database model."""
        return SalesTransactionModel(
            id=entity.id,
            transaction_id=entity.transaction_id,
            invoice_number=entity.invoice_number,
            customer_id=entity.customer_id,
            order_date=entity.order_date,
            delivery_date=entity.delivery_date,
            status=self._map_status_to_db(entity.status),
            payment_status=self._map_payment_status_to_db(entity.payment_status),
            payment_terms=self._map_payment_terms_to_db(entity.payment_terms),
            payment_due_date=entity.payment_due_date,
            subtotal=float(entity.subtotal),
            discount_amount=float(entity.discount_amount),
            tax_amount=float(entity.tax_amount),
            shipping_amount=float(entity.shipping_amount),
            grand_total=float(entity.grand_total),
            amount_paid=float(entity.amount_paid),
            shipping_address=entity.shipping_address,
            billing_address=entity.billing_address,
            purchase_order_number=entity.purchase_order_number,
            sales_person_id=entity.sales_person_id,
            notes=entity.notes,
            customer_notes=entity.customer_notes,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
            is_active=entity.is_active
        )
    
    def _model_to_entity(self, model: SalesTransactionModel) -> SalesTransaction:
        """Convert database model to domain entity."""
        if not model:
            return None
        
        return SalesTransaction(
            id=model.id,
            transaction_id=model.transaction_id,
            invoice_number=model.invoice_number,
            customer_id=model.customer_id,
            order_date=model.order_date,
            delivery_date=model.delivery_date,
            status=self._map_status_from_db(model.status),
            payment_status=self._map_payment_status_from_db(model.payment_status),
            payment_terms=self._map_payment_terms_from_db(model.payment_terms),
            payment_due_date=model.payment_due_date,
            subtotal=Decimal(str(model.subtotal)),
            discount_amount=Decimal(str(model.discount_amount)),
            tax_amount=Decimal(str(model.tax_amount)),
            shipping_amount=Decimal(str(model.shipping_amount)),
            grand_total=Decimal(str(model.grand_total)),
            amount_paid=Decimal(str(model.amount_paid)),
            shipping_address=model.shipping_address,
            billing_address=model.billing_address,
            purchase_order_number=model.purchase_order_number,
            sales_person_id=model.sales_person_id,
            notes=model.notes,
            customer_notes=model.customer_notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            is_active=model.is_active
        )
    
    def _map_status_to_db(self, status: SalesStatus) -> DBSalesStatus:
        """Map domain status to database status."""
        return DBSalesStatus[status.value]
    
    def _map_status_from_db(self, status: DBSalesStatus) -> SalesStatus:
        """Map database status to domain status."""
        return SalesStatus[status.value]
    
    def _map_payment_status_to_db(self, status: PaymentStatus) -> DBPaymentStatus:
        """Map domain payment status to database payment status."""
        return DBPaymentStatus[status.value]
    
    def _map_payment_status_from_db(self, status: DBPaymentStatus) -> PaymentStatus:
        """Map database payment status to domain payment status."""
        return PaymentStatus[status.value]
    
    def _map_payment_terms_to_db(self, terms: PaymentTerms) -> DBPaymentTerms:
        """Map domain payment terms to database payment terms."""
        return DBPaymentTerms[terms.value]
    
    def _map_payment_terms_from_db(self, terms: DBPaymentTerms) -> PaymentTerms:
        """Map database payment terms to domain payment terms."""
        return PaymentTerms[terms.value]