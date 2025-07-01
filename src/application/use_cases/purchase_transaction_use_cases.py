"""Purchase Transaction Use Cases

This module defines use cases for purchase transaction operations.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any

import logging

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem
from src.domain.repositories.purchase_transaction_repository import IPurchaseTransactionRepository
from src.domain.repositories.purchase_transaction_item_repository import IPurchaseTransactionItemRepository
from src.domain.repositories.vendor_repository import VendorRepository
from src.domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from src.domain.repositories.warehouse_repository import WarehouseRepository
from src.domain.repositories.id_manager_repository import IdManagerRepository

logger = logging.getLogger(__name__)


class CreatePurchaseTransactionUseCase:
    """Use case for creating a new purchase transaction."""
    
    PURCHASE_TRANSACTION_PREFIX = 'PUR'
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        vendor_repository: VendorRepository,
        id_manager_repository: IdManagerRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.vendor_repository = vendor_repository
        self.id_manager_repository = id_manager_repository
    
    async def execute(
        self,
        vendor_id: str,
        transaction_date: date,
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> PurchaseTransaction:
        """Create a new purchase transaction."""
        # Validate vendor exists
        vendor = await self.vendor_repository.find_by_id(vendor_id)
        if not vendor:
            raise ValueError(f"Vendor with id {vendor_id} not found")
        
        # Generate transaction ID
        transaction_id = await self._generate_transaction_id()
        
        # Validate transaction ID is unique
        if await self.purchase_repository.exists_by_transaction_id(transaction_id):
            # Retry with new ID
            transaction_id = await self._generate_transaction_id()
        
        # Create purchase transaction
        purchase_transaction = PurchaseTransaction(
            transaction_id=transaction_id,
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            purchase_order_number=purchase_order_number,
            remarks=remarks,
            created_by=created_by
        )
        
        return await self.purchase_repository.create(purchase_transaction)
    
    async def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        next_id = await self.id_manager_repository.get_next_id(
            entity_type="purchase_transaction",
            prefix=self.PURCHASE_TRANSACTION_PREFIX
        )
        return f"{self.PURCHASE_TRANSACTION_PREFIX}-{next_id:06d}"


class CreatePurchaseTransactionWithItemsUseCase:
    """Use case for creating a purchase transaction with items atomically."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        purchase_item_repository: IPurchaseTransactionItemRepository,
        vendor_repository: VendorRepository,
        inventory_repository: InventoryItemMasterRepository,
        warehouse_repository: WarehouseRepository,
        id_manager_repository: IdManagerRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.purchase_item_repository = purchase_item_repository
        self.vendor_repository = vendor_repository
        self.inventory_repository = inventory_repository
        self.warehouse_repository = warehouse_repository
        self.id_manager_repository = id_manager_repository
        self.create_transaction_use_case = CreatePurchaseTransactionUseCase(
            purchase_repository, vendor_repository, id_manager_repository
        )
    
    async def execute(
        self,
        vendor_id: str,
        transaction_date: date,
        items: List[Dict[str, Any]],
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> PurchaseTransaction:
        """Create a purchase transaction with items atomically."""
        # Create the main transaction
        transaction = await self.create_transaction_use_case.execute(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            purchase_order_number=purchase_order_number,
            remarks=remarks,
            created_by=created_by
        )
        
        # Create transaction items
        transaction_items = []
        total_amount = Decimal("0")
        
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
            
            # Validate serial numbers for individually tracked items
            serial_numbers = item_data.get("serial_number", [])
            if inventory_item.tracking_type == "INDIVIDUAL" and serial_numbers:
                # Check serial number uniqueness
                if not await self.purchase_item_repository.validate_serial_numbers_unique(serial_numbers):
                    raise ValueError("One or more serial numbers already exist")
            
            # Create transaction item
            item = PurchaseTransactionItem(
                transaction_id=transaction.id,
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
            total_amount += item.total_price
        
        # Bulk create items
        await self.purchase_item_repository.bulk_create(transaction_items)
        
        # Update transaction totals
        transaction = await self.purchase_repository.update_totals(
            transaction.id,
            total_amount,
            total_amount  # For now, grand_total = total_amount
        )
        
        return transaction


class GetPurchaseTransactionUseCase:
    """Use case for retrieving a purchase transaction."""
    
    def __init__(self, purchase_repository: IPurchaseTransactionRepository):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
    
    async def execute(self, transaction_id: str) -> Optional[PurchaseTransaction]:
        """Get a purchase transaction by ID."""
        return await self.purchase_repository.get_by_id(transaction_id)


class GetPurchaseTransactionByTransactionIdUseCase:
    """Use case for retrieving a purchase transaction by transaction ID."""
    
    def __init__(self, purchase_repository: IPurchaseTransactionRepository):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
    
    async def execute(self, transaction_id: str) -> Optional[PurchaseTransaction]:
        """Get a purchase transaction by transaction ID."""
        return await self.purchase_repository.get_by_transaction_id(transaction_id)


class UpdatePurchaseTransactionUseCase:
    """Use case for updating a purchase transaction."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        vendor_repository: VendorRepository
    ):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
        self.vendor_repository = vendor_repository
    
    async def execute(
        self,
        transaction_id: str,
        vendor_id: Optional[str] = None,
        transaction_date: Optional[date] = None,
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> PurchaseTransaction:
        """Update a purchase transaction."""
        # Get existing transaction
        transaction = await self.purchase_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Purchase transaction with id {transaction_id} not found")
        
        # Check if transaction is editable
        if not transaction.is_editable():
            raise ValueError(f"Cannot edit transaction")
        
        # Validate vendor if provided
        if vendor_id and vendor_id != transaction.vendor_id:
            vendor = await self.vendor_repository.find_by_id(vendor_id)
            if not vendor:
                raise ValueError(f"Vendor with id {vendor_id} not found")
            transaction.vendor_id = vendor_id
        
        # Update fields
        if transaction_date:
            transaction.transaction_date = transaction_date
        
        if purchase_order_number is not None:
            transaction.purchase_order_number = purchase_order_number
        
        if remarks is not None:
            transaction.remarks = remarks
        
        return await self.purchase_repository.update(transaction)




class DeletePurchaseTransactionUseCase:
    """Use case for deleting a purchase transaction."""
    
    def __init__(self, purchase_repository: IPurchaseTransactionRepository):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
    
    async def execute(self, transaction_id: str) -> bool:
        """Delete (soft delete) a purchase transaction."""
        # Get existing transaction
        transaction = await self.purchase_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Purchase transaction with id {transaction_id} not found")
        
        # Check if transaction can be cancelled/deleted
        if not transaction.is_cancellable():
            raise ValueError(f"Cannot delete completed transaction")
        
        return await self.purchase_repository.delete(transaction_id)


class ListPurchaseTransactionsUseCase:
    """Use case for listing purchase transactions with filtering."""
    
    def __init__(self, purchase_repository: IPurchaseTransactionRepository):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
    
    async def execute(
        self,
        page: int = 1,
        page_size: int = 50,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        purchase_order_number: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = True
    ) -> Dict[str, Any]:
        """List purchase transactions with filtering and pagination."""
        skip = (page - 1) * page_size
        
        filters = {}
        if vendor_id:
            filters["vendor_id"] = vendor_id
        if status:
            filters["status"] = status
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        if purchase_order_number:
            filters["purchase_order_number"] = purchase_order_number
        
        transactions = await self.purchase_repository.list(
            skip=skip,
            limit=page_size,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
        
        total_count = await self.purchase_repository.count(filters)
        
        return {
            "transactions": transactions,
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size
        }


class SearchPurchaseTransactionsUseCase:
    """Use case for searching purchase transactions."""
    
    def __init__(self, purchase_repository: IPurchaseTransactionRepository):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
    
    async def execute(
        self,
        query: str,
        vendor_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[PurchaseTransaction]:
        """Search purchase transactions by query."""
        filters = {}
        if vendor_id:
            filters["vendor_id"] = vendor_id
        if status:
            filters["status"] = status
        
        return await self.purchase_repository.search(query, filters)


class GetPurchaseTransactionStatisticsUseCase:
    """Use case for getting purchase transaction statistics."""
    
    def __init__(self, purchase_repository: IPurchaseTransactionRepository):
        """Initialize the use case with required repositories."""
        self.purchase_repository = purchase_repository
    
    async def execute(self) -> Dict[str, Any]:
        """Get purchase transaction statistics."""
        return await self.purchase_repository.get_statistics()