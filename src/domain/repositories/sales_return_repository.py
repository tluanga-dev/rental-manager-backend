"""Sales Return Repository Interface

This module defines the abstract interface for the SalesReturn repository.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.sales import SalesReturn


class ISalesReturnRepository(ABC):
    """Abstract interface for sales return repository operations."""
    
    @abstractmethod
    async def create(self, sales_return: SalesReturn) -> SalesReturn:
        """
        Create a new sales return.
        
        Args:
            sales_return: The sales return entity to create
            
        Returns:
            The created sales return with generated ID
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, return_id: UUID) -> Optional[SalesReturn]:
        """
        Retrieve a sales return by its ID.
        
        Args:
            return_id: The UUID of the sales return
            
        Returns:
            The sales return if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_return_id(self, return_id: str) -> Optional[SalesReturn]:
        """
        Retrieve a sales return by its return ID (e.g., SRT-001).
        
        Args:
            return_id: The return ID string
            
        Returns:
            The sales return if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_transaction(self, sales_transaction_id: UUID) -> List[SalesReturn]:
        """
        Get all returns for a specific sales transaction.
        
        Args:
            sales_transaction_id: The UUID of the sales transaction
            
        Returns:
            List of sales returns
        """
        pass
    
    @abstractmethod
    async def update(self, sales_return: SalesReturn) -> SalesReturn:
        """
        Update an existing sales return.
        
        Args:
            sales_return: The sales return entity with updated data
            
        Returns:
            The updated sales return
        """
        pass
    
    @abstractmethod
    async def delete(self, return_id: UUID) -> bool:
        """
        Soft delete a sales return.
        
        Args:
            return_id: The UUID of the sales return to delete
            
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
    ) -> List[SalesReturn]:
        """
        List sales returns with optional filtering and pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters (date_range, approved_by, etc.)
            sort_by: Field to sort by
            sort_desc: Sort in descending order if True
            
        Returns:
            List of sales returns
        """
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count sales returns with optional filtering.
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Total count of matching sales returns
        """
        pass
    
    @abstractmethod
    async def get_pending_approval(self) -> List[SalesReturn]:
        """
        Get all sales returns pending approval.
        
        Returns:
            List of unapproved sales returns
        """
        pass
    
    @abstractmethod
    async def get_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[SalesReturn]:
        """
        Get sales returns within a date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            List of sales returns within the date range
        """
        pass
    
    @abstractmethod
    async def get_total_refund_amount(self, sales_transaction_id: UUID) -> Decimal:
        """
        Calculate the total refund amount for a sales transaction.
        
        Args:
            sales_transaction_id: The UUID of the sales transaction
            
        Returns:
            Total refund amount across all returns
        """
        pass
    
    @abstractmethod
    async def approve(
        self,
        return_id: UUID,
        approved_by_id: UUID
    ) -> SalesReturn:
        """
        Approve a sales return.
        
        Args:
            return_id: The UUID of the sales return
            approved_by_id: The UUID of the user approving
            
        Returns:
            The updated sales return
        """
        pass
    
    @abstractmethod
    async def exists_by_return_id(self, return_id: str) -> bool:
        """
        Check if a sales return exists with the given return ID.
        
        Args:
            return_id: The return ID to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_return_summary(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Get return summary statistics for a date range.
        
        Args:
            start_date: Start of the date range
            end_date: End of the date range
            
        Returns:
            Dictionary containing summary statistics
        """
        pass