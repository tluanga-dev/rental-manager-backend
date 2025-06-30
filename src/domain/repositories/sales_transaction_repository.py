"""Sales Transaction Repository Interface

This module defines the abstract interface for the SalesTransaction repository.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.sales import SalesTransaction
from src.domain.value_objects.sales import SalesStatus, PaymentStatus


class ISalesTransactionRepository(ABC):
    """Abstract interface for sales transaction repository operations."""
    
    @abstractmethod
    async def create(self, sales_transaction: SalesTransaction) -> SalesTransaction:
        """
        Create a new sales transaction.
        
        Args:
            sales_transaction: The sales transaction entity to create
            
        Returns:
            The created sales transaction with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[SalesTransaction]:
        """
        Retrieve a sales transaction by its ID.
        
        Args:
            transaction_id: The UUID of the sales transaction
            
        Returns:
            The sales transaction if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[SalesTransaction]:
        """
        Retrieve a sales transaction by its transaction ID (e.g., SLS-001).
        
        Args:
            transaction_id: The transaction ID string
            
        Returns:
            The sales transaction if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_invoice_number(self, invoice_number: str) -> Optional[SalesTransaction]:
        """
        Retrieve a sales transaction by its invoice number.
        
        Args:
            invoice_number: The invoice number
            
        Returns:
            The sales transaction if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, sales_transaction: SalesTransaction) -> SalesTransaction:
        """
        Update an existing sales transaction.
        
        Args:
            sales_transaction: The sales transaction entity with updated data
            
        Returns:
            The updated sales transaction
        """
        pass
    
    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        """
        Soft delete a sales transaction.
        
        Args:
            transaction_id: The UUID of the sales transaction to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = True
    ) -> List[SalesTransaction]:
        """
        List sales transactions with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters (customer_id, status, payment_status, date_range, etc.)
            sort_by: Field to sort by
            sort_desc: Sort in descending order if True
            
        Returns:
            List of sales transactions
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count sales transactions with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Total count of matching sales transactions
        """
        pass
    
    @abstractmethod
    async def get_by_customer(
        self,
        customer_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_cancelled: bool = False
    ) -> List[SalesTransaction]:
        """
        Get all sales transactions for a specific customer.
        
        Args:
            customer_id: The customer's UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_cancelled: Whether to include cancelled orders
            
        Returns:
            List of sales transactions for the customer
        """
        pass
    
    @abstractmethod
    async def get_overdue_transactions(
        self,
        as_of_date: Optional[datetime] = None
    ) -> List[SalesTransaction]:
        """
        Get all overdue sales transactions.
        
        Args:
            as_of_date: Check overdue status as of this date (defaults to now)
            
        Returns:
            List of overdue sales transactions
        """
        pass
    
    @abstractmethod
    async def get_pending_delivery(self) -> List[SalesTransaction]:
        """
        Get all sales transactions pending delivery.
        
        Returns:
            List of sales transactions with CONFIRMED or PROCESSING status
        """
        pass
    
    @abstractmethod
    async def get_customer_outstanding_balance(self, customer_id: UUID) -> Decimal:
        """
        Calculate the total outstanding balance for a customer.
        
        Args:
            customer_id: The customer's UUID
            
        Returns:
            Total outstanding balance across all unpaid transactions
        """
        pass
    
    @abstractmethod
    async def get_sales_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get sales summary statistics for a date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            group_by: Optional grouping (e.g., 'day', 'week', 'month', 'customer')
            
        Returns:
            Dictionary containing summary statistics
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        fields: Optional[List[str]] = None
    ) -> List[SalesTransaction]:
        """
        Search sales transactions by text query.
        
        Args:
            query: The search query
            fields: Optional list of fields to search in
            
        Returns:
            List of matching sales transactions
        """
        pass
    
    @abstractmethod
    async def update_payment_status(
        self,
        transaction_id: UUID,
        payment_status: PaymentStatus,
        amount_paid: Decimal
    ) -> SalesTransaction:
        """
        Update the payment status and amount for a transaction.
        
        Args:
            transaction_id: The transaction's UUID
            payment_status: The new payment status
            amount_paid: The total amount paid
            
        Returns:
            The updated sales transaction
        """
        pass
    
    @abstractmethod
    async def update_status(
        self,
        transaction_id: UUID,
        status: SalesStatus
    ) -> SalesTransaction:
        """
        Update the status of a sales transaction.
        
        Args:
            transaction_id: The transaction's UUID
            status: The new status
            
        Returns:
            The updated sales transaction
        """
        pass
    
    @abstractmethod
    async def exists_by_transaction_id(self, transaction_id: str) -> bool:
        """
        Check if a sales transaction exists with the given transaction ID.
        
        Args:
            transaction_id: The transaction ID to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def exists_by_invoice_number(self, invoice_number: str) -> bool:
        """
        Check if a sales transaction exists with the given invoice number.
        
        Args:
            invoice_number: The invoice number to check
            
        Returns:
            True if exists, False otherwise
        """
        pass