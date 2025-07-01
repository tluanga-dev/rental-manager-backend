"""Purchase Transaction Item Use Cases

This module defines use cases for purchase transaction item operations.
"""

from decimal import Decimal
from typing import List, Optional, Dict, Any

import logging

from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem
from src.domain.repositories.purchase_transaction_repository import IPurchaseTransactionRepository
from src.domain.repositories.purchase_transaction_item_repository import IPurchaseTransactionItemRepository
from src.domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from src.domain.repositories.warehouse_repository import WarehouseRepository

logger = logging.getLogger(__name__)


class CreatePurchaseTransactionItemUseCase:
    """Use case for creating a new purchase transaction item."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        purchase_item_repository: IPurchaseTransactionItemRepository,
        inventory_repository: InventoryItemMasterRepository,
        warehouse_repository: WarehouseRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.purchase_item_repository = purchase_item_repository
        self.inventory_repository = inventory_repository
        self.warehouse_repository = warehouse_repository
    
    async def execute(
        self,
        transaction_id: str,
        item_master_id: str,
        quantity: int,
        unit_price: Decimal,
        warehouse_id: Optional[str] = None,
        serial_number: Optional[List[str]] = None,
        discount: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        remarks: Optional[str] = None,
        warranty_period_type: Optional[str] = None,
        warranty_period: Optional[int] = None,
        created_by: Optional[str] = None
    ) -> PurchaseTransactionItem:
        """Create a new purchase transaction item."""
        # Validate transaction exists and can be edited
        transaction = await self.purchase_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Purchase transaction with id {transaction_id} not found")
        
        if not transaction.can_add_items():
            raise ValueError(f"Cannot add items to transaction")
        
        # Validate inventory item exists
        inventory_item = await self.inventory_repository.find_by_id(item_master_id)
        if not inventory_item:
            raise ValueError(f"Inventory item with id {item_master_id} not found")
        
        # Validate warehouse if provided
        if warehouse_id:
            warehouse = await self.warehouse_repository.find_by_id(warehouse_id)
            if not warehouse:
                raise ValueError(f"Warehouse with id {warehouse_id} not found")
        
        # Validate serial numbers if provided
        serial_numbers = serial_number or []
        if serial_numbers:
            if not await self.purchase_item_repository.validate_serial_numbers_unique(serial_numbers):
                raise ValueError("One or more serial numbers already exist")
        
        # Create transaction item
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=item_master_id,
            quantity=quantity,
            unit_price=unit_price,
            warehouse_id=warehouse_id,
            serial_number=serial_numbers,
            discount=discount,
            tax_amount=tax_amount,
            remarks=remarks,
            warranty_period_type=warranty_period_type,
            warranty_period=warranty_period,
            created_by=created_by
        )
        
        # Validate serial numbers for tracking type
        item.validate_serial_numbers_for_tracking_type(inventory_item.tracking_type)
        
        # Create the item
        created_item = await self.purchase_item_repository.create(item)
        
        # Update transaction totals
        await self._update_transaction_totals(transaction_id)
        
        return created_item
    
    async def _update_transaction_totals(self, transaction_id: str) -> None:
        """Update transaction totals based on current items."""
        summary = await self.purchase_item_repository.get_transaction_item_summary(transaction_id)
        total_amount = Decimal(str(summary["total_amount"]))
        
        await self.purchase_repository.update_totals(
            transaction_id,
            total_amount,
            total_amount  # For now, grand_total = total_amount
        )


class BulkCreatePurchaseTransactionItemsUseCase:
    """Use case for creating multiple purchase transaction items atomically."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        purchase_item_repository: IPurchaseTransactionItemRepository,
        inventory_repository: InventoryItemMasterRepository,
        warehouse_repository: WarehouseRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.purchase_item_repository = purchase_item_repository
        self.inventory_repository = inventory_repository
        self.warehouse_repository = warehouse_repository
    
    async def execute(
        self,
        transaction_id: str,
        items: List[Dict[str, Any]],
        created_by: Optional[str] = None
    ) -> List[PurchaseTransactionItem]:
        """Create multiple purchase transaction items atomically."""
        # Validate transaction exists and can be edited
        transaction = await self.purchase_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Purchase transaction with id {transaction_id} not found")
        
        if not transaction.can_add_items():
            raise ValueError(f"Cannot add items to transaction")
        
        # Validate all items first
        transaction_items = []
        all_serial_numbers = []
        
        for item_data in items:
            # Validate inventory item exists
            inventory_item = await self.inventory_repository.find_by_id(item_data["item_master_id"])
            if not inventory_item:
                raise ValueError(f"Inventory item with id {item_data['item_master_id']} not found")
            
            # Validate warehouse if provided
            if item_data.get("warehouse_id"):
                warehouse = await self.warehouse_repository.find_by_id(item_data["warehouse_id"])
                if not warehouse:
                    raise ValueError(f"Warehouse with id {item_data['warehouse_id']} not found")
            
            # Collect serial numbers for bulk validation
            serial_numbers = item_data.get("serial_number", [])
            all_serial_numbers.extend(serial_numbers)
            
            # Create transaction item
            item = PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=item_data["item_master_id"],
                quantity=item_data["quantity"],
                unit_price=Decimal(str(item_data["unit_price"])),
                warehouse_id=item_data.get("warehouse_id"),
                serial_number=serial_numbers,
                discount=Decimal(str(item_data.get("discount", 0))),
                tax_amount=Decimal(str(item_data.get("tax_amount", 0))),
                remarks=item_data.get("remarks"),
                warranty_period_type=item_data.get("warranty_period_type"),
                warranty_period=item_data.get("warranty_period"),
                created_by=created_by
            )
            
            # Validate serial numbers for tracking type
            item.validate_serial_numbers_for_tracking_type(inventory_item.tracking_type)
            
            transaction_items.append(item)
        
        # Validate all serial numbers are unique
        if all_serial_numbers:
            if not await self.purchase_item_repository.validate_serial_numbers_unique(all_serial_numbers):
                raise ValueError("One or more serial numbers already exist")
        
        # Bulk create items
        created_items = await self.purchase_item_repository.bulk_create(transaction_items)
        
        # Update transaction totals
        await self._update_transaction_totals(transaction_id)
        
        return created_items
    
    async def _update_transaction_totals(self, transaction_id: str) -> None:
        """Update transaction totals based on current items."""
        summary = await self.purchase_item_repository.get_transaction_item_summary(transaction_id)
        total_amount = Decimal(str(summary["total_amount"]))
        
        await self.purchase_repository.update_totals(
            transaction_id,
            total_amount,
            total_amount  # For now, grand_total = total_amount
        )


class GetPurchaseTransactionItemUseCase:
    """Use case for retrieving a purchase transaction item."""
    
    def __init__(self, purchase_item_repository: IPurchaseTransactionItemRepository):
        """Initialize the use case with required repositories."""
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(self, item_id: str) -> Optional[PurchaseTransactionItem]:
        """Get a purchase transaction item by ID."""
        return await self.purchase_item_repository.get_by_id(item_id)


class GetPurchaseTransactionItemsByTransactionUseCase:
    """Use case for retrieving items for a purchase transaction."""
    
    def __init__(self, purchase_item_repository: IPurchaseTransactionItemRepository):
        """Initialize the use case with required repositories."""
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(
        self,
        transaction_id: str,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get items for a purchase transaction with pagination."""
        skip = (page - 1) * page_size
        
        items = await self.purchase_item_repository.get_by_transaction_id(
            transaction_id, skip, page_size
        )
        
        total_count = await self.purchase_item_repository.count_by_transaction_id(transaction_id)
        
        return {
            "items": items,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }


class UpdatePurchaseTransactionItemUseCase:
    """Use case for updating a purchase transaction item."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        purchase_item_repository: IPurchaseTransactionItemRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(
        self,
        item_id: str,
        unit_price: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None,
        remarks: Optional[str] = None,
        warranty_period_type: Optional[str] = None,
        warranty_period: Optional[int] = None
    ) -> PurchaseTransactionItem:
        """Update a purchase transaction item."""
        # Get existing item
        item = await self.purchase_item_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"Purchase transaction item with id {item_id} not found")
        
        # Validate transaction can be edited
        transaction = await self.purchase_repository.get_by_id(item.transaction_id)
        if not transaction:
            raise ValueError(f"Purchase transaction with id {item.transaction_id} not found")
        
        if not transaction.is_editable():
            raise ValueError(f"Cannot edit items for transaction")
        
        # Update pricing
        if unit_price is not None or discount is not None or tax_amount is not None:
            item.update_pricing(unit_price, discount, tax_amount)
        
        # Update warranty
        if warranty_period_type is not None or warranty_period is not None:
            item.update_warranty(warranty_period_type, warranty_period)
        
        # Update remarks
        if remarks is not None:
            item.remarks = remarks
        
        # Update the item
        updated_item = await self.purchase_item_repository.update(item)
        
        # Update transaction totals
        await self._update_transaction_totals(item.transaction_id)
        
        return updated_item
    
    async def _update_transaction_totals(self, transaction_id: str) -> None:
        """Update transaction totals based on current items."""
        summary = await self.purchase_item_repository.get_transaction_item_summary(transaction_id)
        total_amount = Decimal(str(summary["total_amount"]))
        
        await self.purchase_repository.update_totals(
            transaction_id,
            total_amount,
            total_amount  # For now, grand_total = total_amount
        )


class DeletePurchaseTransactionItemUseCase:
    """Use case for deleting a purchase transaction item."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        purchase_item_repository: IPurchaseTransactionItemRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(self, item_id: str) -> bool:
        """Delete (soft delete) a purchase transaction item."""
        # Get existing item
        item = await self.purchase_item_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"Purchase transaction item with id {item_id} not found")
        
        # Validate transaction can be edited
        transaction = await self.purchase_repository.get_by_id(item.transaction_id)
        if not transaction:
            raise ValueError(f"Purchase transaction with id {item.transaction_id} not found")
        
        if not transaction.is_editable():
            raise ValueError(f"Cannot delete items for transaction")
        
        # Delete the item
        deleted = await self.purchase_item_repository.delete(item_id)
        
        if deleted:
            # Update transaction totals
            await self._update_transaction_totals(item.transaction_id)
        
        return deleted
    
    async def _update_transaction_totals(self, transaction_id: str) -> None:
        """Update transaction totals based on current items."""
        summary = await self.purchase_item_repository.get_transaction_item_summary(transaction_id)
        total_amount = Decimal(str(summary["total_amount"]))
        
        await self.purchase_repository.update_totals(
            transaction_id,
            total_amount,
            total_amount  # For now, grand_total = total_amount
        )


class GetPurchaseTransactionItemSummaryUseCase:
    """Use case for getting purchase transaction item summary."""
    
    def __init__(self, purchase_item_repository: IPurchaseTransactionItemRepository):
        """Initialize the use case with required repositories."""
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(self, transaction_id: str) -> Dict[str, Any]:
        """Get summary statistics for items in a transaction."""
        return await self.purchase_item_repository.get_transaction_item_summary(transaction_id)


class GetItemsBySerialNumberUseCase:
    """Use case for finding items by serial number."""
    
    def __init__(self, purchase_item_repository: IPurchaseTransactionItemRepository):
        """Initialize the use case with required repositories."""
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(self, serial_number: str) -> Optional[PurchaseTransactionItem]:
        """Find a purchase transaction item by serial number."""
        return await self.purchase_item_repository.get_by_serial_number(serial_number)


class GetItemsWithWarrantyUseCase:
    """Use case for getting items with warranty information."""
    
    def __init__(self, purchase_item_repository: IPurchaseTransactionItemRepository):
        """Initialize the use case with required repositories."""
        self.purchase_item_repository = purchase_item_repository
    
    async def execute(
        self,
        warranty_expiring_before: Optional[str] = None
    ) -> List[PurchaseTransactionItem]:
        """Get all items that have warranty information."""
        return await self.purchase_item_repository.get_items_with_warranty(warranty_expiring_before)