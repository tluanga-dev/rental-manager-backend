"""Sales Transaction Item Repository Interface

This module defines the abstract interface for the SalesTransactionItem repository.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.sales import SalesTransactionItem


class ISalesTransactionItemRepository(ABC):
    """Abstract interface for sales transaction item repository operations."""
    
    @abstractmethod
    async def create(self, item: SalesTransactionItem) -> SalesTransactionItem:
        """
        Create a new sales transaction item.
        
        Args:
            item: The sales transaction item entity to create
            
        Returns:
            The created sales transaction item with generated ID
        """
        pass
    
    @abstractmethod
    async def create_batch(self, items: List[SalesTransactionItem]) -> List[SalesTransactionItem]:
        """
        Create multiple sales transaction items in a batch.
        
        Args:
            items: List of sales transaction item entities to create
            
        Returns:
            List of created sales transaction items
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[SalesTransactionItem]:
        """
        Retrieve a sales transaction item by its ID.
        
        Args:
            item_id: The UUID of the sales transaction item
            
        Returns:
            The sales transaction item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_transaction(self, transaction_id: UUID) -> List[SalesTransactionItem]:
        """
        Get all items for a specific sales transaction.
        
        Args:
            transaction_id: The UUID of the sales transaction
            
        Returns:
            List of sales transaction items
        """
        pass
    
    @abstractmethod
    async def update(self, item: SalesTransactionItem) -> SalesTransactionItem:
        """
        Update an existing sales transaction item.
        
        Args:
            item: The sales transaction item entity with updated data
            
        Returns:
            The updated sales transaction item
        """
        pass
    
    @abstractmethod
    async def update_batch(self, items: List[SalesTransactionItem]) -> List[SalesTransactionItem]:
        """
        Update multiple sales transaction items in a batch.
        
        Args:
            items: List of sales transaction item entities to update
            
        Returns:
            List of updated sales transaction items
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: UUID) -> bool:
        """
        Delete a sales transaction item.
        
        Args:
            item_id: The UUID of the sales transaction item to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_by_transaction(self, transaction_id: UUID) -> int:
        """
        Delete all items for a specific sales transaction.
        
        Args:
            transaction_id: The UUID of the sales transaction
            
        Returns:
            Number of items deleted
        """
        pass
    
    @abstractmethod
    async def get_by_inventory_item(
        self,
        inventory_item_master_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesTransactionItem]:
        """
        Get all sales transaction items for a specific inventory item.
        
        Args:
            inventory_item_master_id: The UUID of the inventory item master
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of sales transaction items
        """
        pass
    
    @abstractmethod
    async def get_by_warehouse(
        self,
        warehouse_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SalesTransactionItem]:
        """
        Get all sales transaction items from a specific warehouse.
        
        Args:
            warehouse_id: The UUID of the warehouse
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of sales transaction items
        """
        pass
    
    @abstractmethod
    async def update_price(
        self,
        item_id: UUID,
        unit_price: Decimal
    ) -> SalesTransactionItem:
        """
        Update the unit price of a sales transaction item.
        
        Args:
            item_id: The UUID of the item
            unit_price: The new unit price
            
        Returns:
            The updated sales transaction item
        """
        pass
    
    @abstractmethod
    async def get_total_quantity_sold(
        self,
        inventory_item_master_id: UUID,
        warehouse_id: Optional[UUID] = None
    ) -> int:
        """
        Get the total quantity sold for an inventory item.
        
        Args:
            inventory_item_master_id: The UUID of the inventory item master
            warehouse_id: Optional warehouse ID to filter by
            
        Returns:
            Total quantity sold
        """
        pass
    
    @abstractmethod
    async def get_sales_by_serial_number(self, serial_number: str) -> Optional[SalesTransactionItem]:
        """
        Find a sales transaction item by serial number.
        
        Args:
            serial_number: The serial number to search for
            
        Returns:
            The sales transaction item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def calculate_transaction_totals(self, transaction_id: UUID) -> Dict[str, Decimal]:
        """
        Calculate totals for all items in a transaction.
        
        Args:
            transaction_id: The UUID of the sales transaction
            
        Returns:
            Dictionary containing subtotal, tax_total, discount_total, and grand_total
        """
        pass