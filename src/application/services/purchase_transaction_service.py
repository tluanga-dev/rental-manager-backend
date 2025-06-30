"""Purchase Transaction Service

This module provides high-level service operations for purchase transactions.
It orchestrates use cases and handles complex business workflows.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from uuid import UUID

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem
from src.domain.repositories.purchase_transaction_repository import IPurchaseTransactionRepository
from src.domain.repositories.purchase_transaction_item_repository import IPurchaseTransactionItemRepository
from src.domain.repositories.vendor_repository import VendorRepository
from src.domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from src.domain.repositories.warehouse_repository import WarehouseRepository
from src.domain.repositories.id_manager_repository import IdManagerRepository
from src.domain.value_objects.purchase.purchase_status import PurchaseStatus

from ..use_cases.purchase_transaction_use_cases import (
    CreatePurchaseTransactionUseCase,
    CreatePurchaseTransactionWithItemsUseCase,
    GetPurchaseTransactionUseCase,
    GetPurchaseTransactionByTransactionIdUseCase,
    UpdatePurchaseTransactionUseCase,
    UpdatePurchaseTransactionStatusUseCase,
    DeletePurchaseTransactionUseCase,
    ListPurchaseTransactionsUseCase,
    SearchPurchaseTransactionsUseCase,
    GetPurchaseTransactionStatisticsUseCase
)

from ..use_cases.purchase_transaction_item_use_cases import (
    CreatePurchaseTransactionItemUseCase,
    BulkCreatePurchaseTransactionItemsUseCase,
    GetPurchaseTransactionItemUseCase,
    GetPurchaseTransactionItemsByTransactionUseCase,
    UpdatePurchaseTransactionItemUseCase,
    DeletePurchaseTransactionItemUseCase,
    GetPurchaseTransactionItemSummaryUseCase,
    GetItemsBySerialNumberUseCase,
    GetItemsWithWarrantyUseCase
)


class PurchaseTransactionService:
    """Service for purchase transaction operations."""
    
    def __init__(
        self,
        purchase_repository: IPurchaseTransactionRepository,
        purchase_item_repository: IPurchaseTransactionItemRepository,
        vendor_repository: VendorRepository,
        inventory_repository: InventoryItemMasterRepository,
        warehouse_repository: WarehouseRepository,
        id_manager_repository: IdManagerRepository
    ) -> None:
        """Initialize the service with required repositories."""
        self.purchase_repository = purchase_repository
        self.purchase_item_repository = purchase_item_repository
        self.vendor_repository = vendor_repository
        self.inventory_repository = inventory_repository
        self.warehouse_repository = warehouse_repository
        self.id_manager_repository = id_manager_repository
        
        # Initialize use cases
        self._init_transaction_use_cases()
        self._init_item_use_cases()
    
    def _init_transaction_use_cases(self) -> None:
        """Initialize transaction-related use cases."""
        self.create_transaction_use_case = CreatePurchaseTransactionUseCase(
            self.purchase_repository,
            self.vendor_repository,
            self.id_manager_repository
        )
        
        self.create_transaction_with_items_use_case = CreatePurchaseTransactionWithItemsUseCase(
            self.purchase_repository,
            self.purchase_item_repository,
            self.vendor_repository,
            self.inventory_repository,
            self.warehouse_repository,
            self.id_manager_repository
        )
        
        self.get_transaction_use_case = GetPurchaseTransactionUseCase(
            self.purchase_repository
        )
        
        self.get_transaction_by_transaction_id_use_case = GetPurchaseTransactionByTransactionIdUseCase(
            self.purchase_repository
        )
        
        self.update_transaction_use_case = UpdatePurchaseTransactionUseCase(
            self.purchase_repository,
            self.vendor_repository
        )
        
        self.update_transaction_status_use_case = UpdatePurchaseTransactionStatusUseCase(
            self.purchase_repository
        )
        
        self.delete_transaction_use_case = DeletePurchaseTransactionUseCase(
            self.purchase_repository
        )
        
        self.list_transactions_use_case = ListPurchaseTransactionsUseCase(
            self.purchase_repository
        )
        
        self.search_transactions_use_case = SearchPurchaseTransactionsUseCase(
            self.purchase_repository
        )
        
        self.get_statistics_use_case = GetPurchaseTransactionStatisticsUseCase(
            self.purchase_repository
        )
    
    def _init_item_use_cases(self) -> None:
        """Initialize item-related use cases."""
        self.create_item_use_case = CreatePurchaseTransactionItemUseCase(
            self.purchase_repository,
            self.purchase_item_repository,
            self.inventory_repository,
            self.warehouse_repository
        )
        
        self.bulk_create_items_use_case = BulkCreatePurchaseTransactionItemsUseCase(
            self.purchase_repository,
            self.purchase_item_repository,
            self.inventory_repository,
            self.warehouse_repository
        )
        
        self.get_item_use_case = GetPurchaseTransactionItemUseCase(
            self.purchase_item_repository
        )
        
        self.get_items_by_transaction_use_case = GetPurchaseTransactionItemsByTransactionUseCase(
            self.purchase_item_repository
        )
        
        self.update_item_use_case = UpdatePurchaseTransactionItemUseCase(
            self.purchase_repository,
            self.purchase_item_repository
        )
        
        self.delete_item_use_case = DeletePurchaseTransactionItemUseCase(
            self.purchase_repository,
            self.purchase_item_repository
        )
        
        self.get_item_summary_use_case = GetPurchaseTransactionItemSummaryUseCase(
            self.purchase_item_repository
        )
        
        self.get_items_by_serial_number_use_case = GetItemsBySerialNumberUseCase(
            self.purchase_item_repository
        )
        
        self.get_items_with_warranty_use_case = GetItemsWithWarrantyUseCase(
            self.purchase_item_repository
        )
    
    # Transaction methods
    
    async def create_transaction(
        self,
        vendor_id: UUID,
        transaction_date: date,
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> PurchaseTransaction:
        """Create a new purchase transaction."""
        return await self.create_transaction_use_case.execute(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            purchase_order_number=purchase_order_number,
            remarks=remarks,
            created_by=created_by
        )
    
    async def create_transaction_with_items(
        self,
        vendor_id: UUID,
        transaction_date: date,
        items: List[Dict[str, Any]],
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> PurchaseTransaction:
        """Create a purchase transaction with items atomically."""
        return await self.create_transaction_with_items_use_case.execute(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            items=items,
            purchase_order_number=purchase_order_number,
            remarks=remarks,
            created_by=created_by
        )
    
    async def get_transaction(self, transaction_id: UUID) -> Optional[PurchaseTransaction]:
        """Get a purchase transaction by ID."""
        return await self.get_transaction_use_case.execute(transaction_id)
    
    async def get_transaction_by_transaction_id(self, transaction_id: str) -> Optional[PurchaseTransaction]:
        """Get a purchase transaction by transaction ID."""
        return await self.get_transaction_by_transaction_id_use_case.execute(transaction_id)
    
    async def get_transaction_with_items(self, transaction_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a purchase transaction with its items."""
        transaction = await self.get_transaction(transaction_id)
        if not transaction:
            return None
        
        items_result = await self.get_items_by_transaction_use_case.execute(
            transaction_id, page=1, page_size=1000  # Get all items
        )
        
        return {
            "transaction": transaction,
            "items": items_result["items"],
            "item_summary": await self.get_item_summary_use_case.execute(transaction_id)
        }
    
    async def update_transaction(
        self,
        transaction_id: UUID,
        vendor_id: Optional[UUID] = None,
        transaction_date: Optional[date] = None,
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None
    ) -> PurchaseTransaction:
        """Update a purchase transaction."""
        return await self.update_transaction_use_case.execute(
            transaction_id=transaction_id,
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            purchase_order_number=purchase_order_number,
            remarks=remarks
        )
    
    async def update_transaction_status(
        self,
        transaction_id: UUID,
        new_status: PurchaseStatus
    ) -> PurchaseTransaction:
        """Update purchase transaction status."""
        return await self.update_transaction_status_use_case.execute(
            transaction_id, new_status
        )
    
    async def delete_transaction(self, transaction_id: UUID) -> bool:
        """Delete (soft delete) a purchase transaction."""
        return await self.delete_transaction_use_case.execute(transaction_id)
    
    async def list_transactions(
        self,
        page: int = 1,
        page_size: int = 50,
        vendor_id: Optional[UUID] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        purchase_order_number: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = True
    ) -> Dict[str, Any]:
        """List purchase transactions with filtering and pagination."""
        return await self.list_transactions_use_case.execute(
            page=page,
            page_size=page_size,
            vendor_id=vendor_id,
            status=status,
            date_from=date_from,
            date_to=date_to,
            purchase_order_number=purchase_order_number,
            sort_by=sort_by,
            sort_desc=sort_desc
        )
    
    async def search_transactions(
        self,
        query: str,
        vendor_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[PurchaseTransaction]:
        """Search purchase transactions by query."""
        return await self.search_transactions_use_case.execute(
            query=query,
            vendor_id=vendor_id,
            status=status
        )
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get purchase transaction statistics."""
        return await self.get_statistics_use_case.execute()
    
    # Item methods
    
    async def create_item(
        self,
        transaction_id: UUID,
        item_master_id: UUID,
        quantity: int,
        unit_price: Decimal,
        warehouse_id: Optional[UUID] = None,
        serial_number: Optional[List[str]] = None,
        discount: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        remarks: Optional[str] = None,
        warranty_period_type: Optional[str] = None,
        warranty_period: Optional[int] = None,
        created_by: Optional[str] = None
    ) -> PurchaseTransactionItem:
        """Create a new purchase transaction item."""
        return await self.create_item_use_case.execute(
            transaction_id=transaction_id,
            item_master_id=item_master_id,
            quantity=quantity,
            unit_price=unit_price,
            warehouse_id=warehouse_id,
            serial_number=serial_number,
            discount=discount,
            tax_amount=tax_amount,
            remarks=remarks,
            warranty_period_type=warranty_period_type,
            warranty_period=warranty_period,
            created_by=created_by
        )
    
    async def bulk_create_items(
        self,
        transaction_id: UUID,
        items: List[Dict[str, Any]],
        created_by: Optional[str] = None
    ) -> List[PurchaseTransactionItem]:
        """Create multiple purchase transaction items atomically."""
        return await self.bulk_create_items_use_case.execute(
            transaction_id=transaction_id,
            items=items,
            created_by=created_by
        )
    
    async def get_item(self, item_id: UUID) -> Optional[PurchaseTransactionItem]:
        """Get a purchase transaction item by ID."""
        return await self.get_item_use_case.execute(item_id)
    
    async def get_items_by_transaction(
        self,
        transaction_id: UUID,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """Get items for a purchase transaction with pagination."""
        return await self.get_items_by_transaction_use_case.execute(
            transaction_id=transaction_id,
            page=page,
            page_size=page_size
        )
    
    async def update_item(
        self,
        item_id: UUID,
        unit_price: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None,
        remarks: Optional[str] = None,
        warranty_period_type: Optional[str] = None,
        warranty_period: Optional[int] = None
    ) -> PurchaseTransactionItem:
        """Update a purchase transaction item."""
        return await self.update_item_use_case.execute(
            item_id=item_id,
            unit_price=unit_price,
            discount=discount,
            tax_amount=tax_amount,
            remarks=remarks,
            warranty_period_type=warranty_period_type,
            warranty_period=warranty_period
        )
    
    async def delete_item(self, item_id: UUID) -> bool:
        """Delete (soft delete) a purchase transaction item."""
        return await self.delete_item_use_case.execute(item_id)
    
    async def get_item_summary(self, transaction_id: UUID) -> Dict[str, Any]:
        """Get summary statistics for items in a transaction."""
        return await self.get_item_summary_use_case.execute(transaction_id)
    
    async def get_item_by_serial_number(self, serial_number: str) -> Optional[PurchaseTransactionItem]:
        """Find a purchase transaction item by serial number."""
        return await self.get_items_by_serial_number_use_case.execute(serial_number)
    
    async def get_items_with_warranty(
        self,
        warranty_expiring_before: Optional[str] = None
    ) -> List[PurchaseTransactionItem]:
        """Get all items that have warranty information."""
        return await self.get_items_with_warranty_use_case.execute(warranty_expiring_before)
    
    # Workflow methods
    
    async def confirm_transaction(self, transaction_id: UUID) -> PurchaseTransaction:
        """Confirm a draft transaction."""
        return await self.update_transaction_status(transaction_id, PurchaseStatus.CONFIRMED)
    
    async def start_processing(self, transaction_id: UUID) -> PurchaseTransaction:
        """Start processing a confirmed transaction."""
        return await self.update_transaction_status(transaction_id, PurchaseStatus.PROCESSING)
    
    async def mark_as_received(self, transaction_id: UUID) -> PurchaseTransaction:
        """Mark a processing transaction as received."""
        return await self.update_transaction_status(transaction_id, PurchaseStatus.RECEIVED)
    
    async def complete_transaction(self, transaction_id: UUID) -> PurchaseTransaction:
        """Complete a received transaction."""
        return await self.update_transaction_status(transaction_id, PurchaseStatus.COMPLETED)
    
    async def cancel_transaction(self, transaction_id: UUID) -> PurchaseTransaction:
        """Cancel a transaction."""
        return await self.update_transaction_status(transaction_id, PurchaseStatus.CANCELLED)