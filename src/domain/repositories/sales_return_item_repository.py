"""Sales Return Item Repository Interface

This module defines the abstract interface for the SalesReturnItem repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.sales import SalesReturnItem


class ISalesReturnItemRepository(ABC):
    """Abstract interface for sales return item repository operations."""
    
    @abstractmethod
    async def create(self, item: SalesReturnItem) -> SalesReturnItem:
        """
        Create a new sales return item.
        
        Args:
            item: The sales return item entity to create
            
        Returns:
            The created sales return item with generated ID
        """
        pass
    
    @abstractmethod
    async def create_batch(self, items: List[SalesReturnItem]) -> List[SalesReturnItem]:
        """
        Create multiple sales return items in a batch.
        
        Args:
            items: List of sales return item entities to create
            
        Returns:
            List of created sales return items
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[SalesReturnItem]:
        """
        Retrieve a sales return item by its ID.
        
        Args:
            item_id: The UUID of the sales return item
            
        Returns:
            The sales return item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_return(self, sales_return_id: UUID) -> List[SalesReturnItem]:
        """
        Get all items for a specific sales return.
        
        Args:
            sales_return_id: The UUID of the sales return
            
        Returns:
            List of sales return items
        """
        pass
    
    @abstractmethod
    async def get_by_sales_item(self, sales_item_id: UUID) -> List[SalesReturnItem]:
        """
        Get all return items for a specific sales transaction item.
        
        Args:
            sales_item_id: The UUID of the original sales transaction item
            
        Returns:
            List of sales return items
        """
        pass
    
    @abstractmethod
    async def update(self, item: SalesReturnItem) -> SalesReturnItem:
        """
        Update an existing sales return item.
        
        Args:
            item: The sales return item entity with updated data
            
        Returns:
            The updated sales return item
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: UUID) -> bool:
        """
        Delete a sales return item.
        
        Args:
            item_id: The UUID of the sales return item to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_by_return(self, sales_return_id: UUID) -> int:
        """
        Delete all items for a specific sales return.
        
        Args:
            sales_return_id: The UUID of the sales return
            
        Returns:
            Number of items deleted
        """
        pass
    
    @abstractmethod
    async def get_total_returned_quantity(self, sales_item_id: UUID) -> int:
        """
        Get the total quantity returned for a sales transaction item.
        
        Args:
            sales_item_id: The UUID of the original sales transaction item
            
        Returns:
            Total quantity returned
        """
        pass
    
    @abstractmethod
    async def get_by_serial_number(self, serial_number: str) -> Optional[SalesReturnItem]:
        """
        Find a sales return item by serial number.
        
        Args:
            serial_number: The serial number to search for
            
        Returns:
            The sales return item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_resellable_items(self, warehouse_id: Optional[UUID] = None) -> List[SalesReturnItem]:
        """
        Get all return items that are in resellable condition.
        
        Args:
            warehouse_id: Optional warehouse ID to filter by
            
        Returns:
            List of resellable return items
        """
        pass