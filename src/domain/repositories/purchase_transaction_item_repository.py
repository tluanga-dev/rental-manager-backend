"""Purchase Transaction Item Repository Interface

This module defines the abstract interface for the PurchaseTransactionItem repository.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem


class IPurchaseTransactionItemRepository(ABC):
    """Abstract interface for purchase transaction item repository operations."""
    
    @abstractmethod
    async def create(self, item: PurchaseTransactionItem) -> PurchaseTransactionItem:
        """
        Create a new purchase transaction item.
        
        Args:
            item: The purchase transaction item entity to create
            
        Returns:
            The created item with generated ID
        """
        pass
    
    @abstractmethod
    async def bulk_create(self, items: List[PurchaseTransactionItem]) -> List[PurchaseTransactionItem]:
        """
        Create multiple purchase transaction items atomically.
        
        Args:
            items: List of purchase transaction item entities to create
            
        Returns:
            List of created items with generated IDs
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Optional[PurchaseTransactionItem]:
        """
        Retrieve a purchase transaction item by its ID.
        
        Args:
            item_id: The UUID of the purchase transaction item
            
        Returns:
            The purchase transaction item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_transaction_id(
        self,
        transaction_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseTransactionItem]:
        """
        Get all items for a specific purchase transaction.
        
        Args:
            transaction_id: The transaction's UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of purchase transaction items
        """
        pass
    
    @abstractmethod
    async def update(self, item: PurchaseTransactionItem) -> PurchaseTransactionItem:
        """
        Update an existing purchase transaction item.
        
        Args:
            item: The purchase transaction item entity with updated data
            
        Returns:
            The updated item
        """
        pass
    
    @abstractmethod
    async def delete(self, item_id: UUID) -> bool:
        """
        Soft delete a purchase transaction item.
        
        Args:
            item_id: The UUID of the item to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def count_by_transaction_id(self, transaction_id: UUID) -> int:
        """
        Count items for a specific purchase transaction.
        
        Args:
            transaction_id: The transaction's UUID
            
        Returns:
            Total count of items for the transaction
        """
        pass
    
    @abstractmethod
    async def get_by_inventory_item_id(
        self,
        inventory_item_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseTransactionItem]:
        """
        Get all purchase transaction items for a specific inventory item.
        
        Args:
            inventory_item_id: The inventory item's UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of purchase transaction items
        """
        pass
    
    @abstractmethod
    async def get_by_warehouse_id(
        self,
        warehouse_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[PurchaseTransactionItem]:
        """
        Get all purchase transaction items for a specific warehouse.
        
        Args:
            warehouse_id: The warehouse's UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of purchase transaction items
        """
        pass
    
    @abstractmethod
    async def get_by_serial_number(self, serial_number: str) -> Optional[PurchaseTransactionItem]:
        """
        Find a purchase transaction item by serial number.
        
        Args:
            serial_number: The serial number to search for
            
        Returns:
            The purchase transaction item if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def check_serial_number_exists(self, serial_number: str) -> bool:
        """
        Check if a serial number already exists in any purchase transaction item.
        
        Args:
            serial_number: The serial number to check
            
        Returns:
            True if serial number exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_serial_numbers_unique(self, serial_numbers: List[str]) -> bool:
        """
        Validate that all provided serial numbers are unique across the system.
        
        Args:
            serial_numbers: List of serial numbers to validate
            
        Returns:
            True if all serial numbers are unique, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_transaction_item_summary(self, transaction_id: UUID) -> Dict[str, Any]:
        """
        Get summary statistics for all items in a transaction.
        
        Args:
            transaction_id: The transaction's UUID
            
        Returns:
            Dictionary containing summary data (total items, total cost, etc.)
        """
        pass
    
    @abstractmethod
    async def update_pricing(
        self,
        item_id: UUID,
        unit_price: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None
    ) -> PurchaseTransactionItem:
        """
        Update pricing information for an item.
        
        Args:
            item_id: The item's UUID
            unit_price: New unit price
            discount: New discount amount
            tax_amount: New tax amount
            
        Returns:
            The updated purchase transaction item
        """
        pass
    
    @abstractmethod
    async def get_items_with_warranty(
        self,
        warranty_expiring_before: Optional[str] = None
    ) -> List[PurchaseTransactionItem]:
        """
        Get all items that have warranty information.
        
        Args:
            warranty_expiring_before: Optional date to filter items with warranty expiring before this date
            
        Returns:
            List of items with warranty information
        """
        pass