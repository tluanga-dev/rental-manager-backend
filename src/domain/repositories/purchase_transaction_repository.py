"""Purchase Transaction Repository Interface

This module defines the abstract interface for the PurchaseTransaction repository.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.value_objects.purchase.purchase_status import PurchaseStatus


class IPurchaseTransactionRepository(ABC):
    """Abstract interface for purchase transaction repository operations."""
    
    @abstractmethod
    async def create(self, purchase_transaction: PurchaseTransaction) -> PurchaseTransaction:
        """
        Create a new purchase transaction.
        
        Args:
            purchase_transaction: The purchase transaction entity to create
            
        Returns:
            The created purchase transaction with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, transaction_id: UUID) -> Optional[PurchaseTransaction]:
        """
        Retrieve a purchase transaction by its ID.
        
        Args:
            transaction_id: The UUID of the purchase transaction
            
        Returns:
            The purchase transaction if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_transaction_id(self, transaction_id: str) -> Optional[PurchaseTransaction]:
        """
        Retrieve a purchase transaction by its transaction ID (e.g., PUR-001).
        
        Args:
            transaction_id: The transaction ID string
            
        Returns:
            The purchase transaction if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, purchase_transaction: PurchaseTransaction) -> PurchaseTransaction:
        """
        Update an existing purchase transaction.
        
        Args:
            purchase_transaction: The purchase transaction entity with updated data
            
        Returns:
            The updated purchase transaction
        """
        pass
    
    @abstractmethod
    async def delete(self, transaction_id: UUID) -> bool:
        """
        Soft delete a purchase transaction.
        
        Args:
            transaction_id: The UUID of the purchase transaction to delete
            
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
    ) -> List[PurchaseTransaction]:
        """
        List purchase transactions with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters (vendor_id, status, date_range, etc.)
            sort_by: Field to sort by
            sort_desc: Sort in descending order if True
            
        Returns:
            List of purchase transactions
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count purchase transactions with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Total count of matching purchase transactions
        """
        pass
    
    @abstractmethod
    async def get_by_vendor(
        self,
        vendor_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_cancelled: bool = False
    ) -> List[PurchaseTransaction]:
        """
        Get all purchase transactions for a specific vendor.
        
        Args:
            vendor_id: The vendor's UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_cancelled: Whether to include cancelled transactions
            
        Returns:
            List of purchase transactions for the vendor
        """
        pass
    
    @abstractmethod
    async def get_by_purchase_order_number(
        self, 
        purchase_order_number: str
    ) -> Optional[PurchaseTransaction]:
        """
        Get purchase transaction by purchase order number.
        
        Args:
            purchase_order_number: The purchase order number
            
        Returns:
            The purchase transaction if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_pending_transactions(self) -> List[PurchaseTransaction]:
        """
        Get all purchase transactions that are pending processing.
        
        Returns:
            List of purchase transactions with DRAFT or CONFIRMED status
        """
        pass
    
    @abstractmethod
    async def get_in_progress_transactions(self) -> List[PurchaseTransaction]:
        """
        Get all purchase transactions currently in progress.
        
        Returns:
            List of purchase transactions with PROCESSING or RECEIVED status
        """
        pass
    
    @abstractmethod
    async def get_purchase_summary(
        self,
        start_date: date,
        end_date: date,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get purchase summary statistics for a date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            group_by: Optional grouping (e.g., 'day', 'week', 'month', 'vendor')
            
        Returns:
            Dictionary containing summary statistics
        """
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[PurchaseTransaction]:
        """
        Search purchase transactions by text query.
        
        Args:
            query: The search query
            filters: Optional additional filters
            
        Returns:
            List of matching purchase transactions
        """
        pass
    
    @abstractmethod
    async def update_status(
        self,
        transaction_id: UUID,
        status: PurchaseStatus
    ) -> PurchaseTransaction:
        """
        Update the status of a purchase transaction.
        
        Args:
            transaction_id: The transaction's UUID
            status: The new status
            
        Returns:
            The updated purchase transaction
        """
        pass
    
    @abstractmethod
    async def update_totals(
        self,
        transaction_id: UUID,
        total_amount: Decimal,
        grand_total: Decimal
    ) -> PurchaseTransaction:
        """
        Update the totals of a purchase transaction.
        
        Args:
            transaction_id: The transaction's UUID
            total_amount: The new total amount
            grand_total: The new grand total
            
        Returns:
            The updated purchase transaction
        """
        pass
    
    @abstractmethod
    async def exists_by_transaction_id(self, transaction_id: str) -> bool:
        """
        Check if a purchase transaction exists with the given transaction ID.
        
        Args:
            transaction_id: The transaction ID to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get general purchase transaction statistics.
        
        Returns:
            Dictionary containing various statistics
        """
        pass