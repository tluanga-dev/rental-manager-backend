"""
Unit tests for Purchase Transaction Application Layer.

Tests the business orchestration and use cases with mocked dependencies:
- Purchase transaction use cases
- Purchase transaction item use cases  
- Purchase transaction service
- Business workflow validation
- Error handling and edge cases
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4
from typing import List, Dict, Any, Optional

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem
from src.domain.entities.vendor import Vendor
from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.domain.entities.warehouse import Warehouse
from src.domain.entities.id_manager import IdManager

from src.application.use_cases.purchase_transaction_use_cases import (
    CreatePurchaseTransactionUseCase,
    CreatePurchaseTransactionWithItemsUseCase,
    GetPurchaseTransactionUseCase,
    GetPurchaseTransactionByTransactionIdUseCase,
    UpdatePurchaseTransactionUseCase,
    DeletePurchaseTransactionUseCase,
    ListPurchaseTransactionsUseCase,
    SearchPurchaseTransactionsUseCase,
    GetPurchaseTransactionStatisticsUseCase
)

from src.application.use_cases.purchase_transaction_item_use_cases import (
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

from src.application.services.purchase_transaction_service import PurchaseTransactionService


class TestCreatePurchaseTransactionUseCase:
    """Test create purchase transaction use case."""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories."""
        purchase_repository = AsyncMock()
        vendor_repository = AsyncMock()
        id_manager_repository = AsyncMock()
        return purchase_repository, vendor_repository, id_manager_repository
    
    @pytest.fixture
    def use_case(self, mock_repositories):
        """Create use case with mocked dependencies."""
        purchase_repo, vendor_repo, id_manager_repo = mock_repositories
        return CreatePurchaseTransactionUseCase(
            purchase_repository=purchase_repo,
            vendor_repository=vendor_repo,
            id_manager_repository=id_manager_repo
        ), purchase_repo, vendor_repo, id_manager_repo
    
    @pytest.mark.asyncio
    async def test_create_transaction_success(self, use_case):
        """Test successful transaction creation."""
        use_case_instance, purchase_repo, vendor_repo, id_manager_repo = use_case
        
        # Setup test data
        vendor_id = str(uuid4())
        transaction_date = date.today()
        created_by = "test_user"
        
        # Mock vendor exists
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        
        # Mock ID generation
        id_manager_repo.get_next_id.return_value = 1
        
        # Mock transaction creation
        expected_transaction = PurchaseTransaction(
            transaction_id="PUR-000001",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            created_by=created_by
        )
        purchase_repo.create.return_value = expected_transaction
        purchase_repo.exists_by_transaction_id.return_value = False
        
        # Execute use case
        result = await use_case_instance.execute(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            created_by=created_by
        )
        
        # Verify interactions
        vendor_repo.find_by_id.assert_called_once_with(vendor_id)
        id_manager_repo.get_next_id.assert_called_once_with(
            entity_type="purchase_transaction",
            prefix="PUR"
        )
        purchase_repo.exists_by_transaction_id.assert_called_once()
        purchase_repo.create.assert_called_once()
        
        # Verify result
        assert result.transaction_id == "PUR-000001"
        assert result.vendor_id == vendor_id
        assert result.transaction_date == transaction_date
        assert result.created_by == created_by
    
    @pytest.mark.asyncio
    async def test_create_transaction_vendor_not_found(self, use_case):
        """Test transaction creation with non-existent vendor."""
        use_case_instance, purchase_repo, vendor_repo, id_manager_repo = use_case
        
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        # Mock vendor not found
        vendor_repo.find_by_id.return_value = None
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match=f"Vendor with id {vendor_id} not found"):
            await use_case_instance.execute(
                vendor_id=vendor_id,
                transaction_date=transaction_date
            )
        
        # Verify vendor lookup was attempted
        vendor_repo.find_by_id.assert_called_once_with(vendor_id)
        # Verify no transaction was created
        purchase_repo.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_transaction_with_duplicate_id_retry(self, use_case):
        """Test transaction creation with duplicate ID requiring retry."""
        use_case_instance, purchase_repo, vendor_repo, id_manager_repo = use_case
        
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        # Mock vendor exists
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        
        # Mock ID generation (called twice for retry)
        id_manager_repo.get_next_id.side_effect = [1, 2]
        
        # Mock first transaction ID exists, second doesn't
        purchase_repo.exists_by_transaction_id.side_effect = [True, False]
        
        # Mock transaction creation
        expected_transaction = PurchaseTransaction(
            transaction_id="PUR-000002",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        purchase_repo.create.return_value = expected_transaction
        
        # Execute use case
        result = await use_case_instance.execute(
            vendor_id=vendor_id,
            transaction_date=transaction_date
        )
        
        # Verify ID generation was called twice
        assert id_manager_repo.get_next_id.call_count == 2
        # Verify existence check was called once (for first ID)
        assert purchase_repo.exists_by_transaction_id.call_count == 1
        # Verify final transaction uses second ID
        assert result.transaction_id == "PUR-000002"


class TestCreatePurchaseTransactionWithItemsUseCase:
    """Test create purchase transaction with items use case."""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories."""
        purchase_repository = AsyncMock()
        purchase_item_repository = AsyncMock()
        vendor_repository = AsyncMock()
        inventory_repository = AsyncMock()
        warehouse_repository = AsyncMock()
        id_manager_repository = AsyncMock()
        return (purchase_repository, purchase_item_repository, vendor_repository, 
                inventory_repository, warehouse_repository, id_manager_repository)
    
    @pytest.fixture
    def use_case(self, mock_repositories):
        """Create use case with mocked dependencies."""
        (purchase_repo, purchase_item_repo, vendor_repo, 
         inventory_repo, warehouse_repo, id_manager_repo) = mock_repositories
        
        return CreatePurchaseTransactionWithItemsUseCase(
            purchase_repository=purchase_repo,
            purchase_item_repository=purchase_item_repo,
            vendor_repository=vendor_repo,
            inventory_repository=inventory_repo,
            warehouse_repository=warehouse_repo,
            id_manager_repository=id_manager_repo
        ), purchase_repo, purchase_item_repo, vendor_repo, inventory_repo, warehouse_repo, id_manager_repo
    
    @pytest.mark.asyncio
    async def test_create_transaction_with_items_success(self, use_case):
        """Test successful transaction creation with items."""
        (use_case_instance, purchase_repo, purchase_item_repo, vendor_repo, 
         inventory_repo, warehouse_repo, id_manager_repo) = use_case
        
        # Setup test data
        vendor_id = str(uuid4())
        warehouse_id = str(uuid4())
        item_master_id = str(uuid4())
        transaction_date = date.today()
        created_by = "test_user"
        
        items_data = [
            {
                "item_master_id": item_master_id,
                "quantity": 2,
                "unit_price": "100.00",
                "warehouse_id": warehouse_id,
                "serial_number": ["SN001", "SN002"],
                "discount": "10.00",
                "tax_amount": "15.00"
            }
        ]
        
        # Mock vendor exists
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        
        # Mock ID generation
        id_manager_repo.get_next_id.return_value = 1
        
        # Mock inventory item exists
        mock_inventory_item = MagicMock()
        mock_inventory_item.tracking_type = "INDIVIDUAL"
        inventory_repo.find_by_id.return_value = mock_inventory_item
        
        # Mock warehouse exists
        mock_warehouse = MagicMock()
        warehouse_repo.find_by_id.return_value = mock_warehouse
        
        # Mock transaction creation
        transaction_id = str(uuid4())
        expected_transaction = PurchaseTransaction(
            entity_id=transaction_id,
            transaction_id="PUR-000001",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            created_by=created_by
        )
        purchase_repo.create.return_value = expected_transaction
        purchase_repo.exists_by_transaction_id.return_value = False
        
        # Mock item creation
        expected_items = [
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=item_master_id,
                quantity=2,
                unit_price=Decimal("100.00"),
                warehouse_id=warehouse_id,
                serial_number=["SN001", "SN002"],
                discount=Decimal("10.00"),
                tax_amount=Decimal("15.00")
            )
        ]
        purchase_item_repo.bulk_create.return_value = expected_items
        purchase_item_repo.validate_serial_numbers_unique.return_value = True
        
        # Mock totals update
        updated_transaction = PurchaseTransaction(
            entity_id=transaction_id,
            transaction_id="PUR-000001",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            total_amount=Decimal("205.00"),  # (2 * 100.00) - 10.00 + 15.00
            grand_total=Decimal("205.00"),
            created_by=created_by
        )
        purchase_repo.update_totals.return_value = updated_transaction
        
        # Execute use case
        result = await use_case_instance.execute(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            items=items_data,
            created_by=created_by
        )
        
        # Verify interactions
        vendor_repo.find_by_id.assert_called_once_with(vendor_id)
        inventory_repo.find_by_id.assert_called_once_with(item_master_id)
        warehouse_repo.find_by_id.assert_called_once_with(warehouse_id)
        purchase_item_repo.validate_serial_numbers_unique.assert_called_once()
        purchase_item_repo.bulk_create.assert_called_once()
        purchase_repo.update_totals.assert_called_once()
        
        # Verify result
        assert result.transaction_id == "PUR-000001"
        assert result.total_amount == Decimal("205.00")
        assert result.grand_total == Decimal("205.00")
    
    @pytest.mark.asyncio
    async def test_create_transaction_with_items_inventory_not_found(self, use_case):
        """Test transaction creation with non-existent inventory item."""
        (use_case_instance, purchase_repo, purchase_item_repo, vendor_repo, 
         inventory_repo, warehouse_repo, id_manager_repo) = use_case
        
        vendor_id = str(uuid4())
        item_master_id = str(uuid4())
        transaction_date = date.today()
        
        items_data = [
            {
                "item_master_id": item_master_id,
                "quantity": 1,
                "unit_price": "100.00"
            }
        ]
        
        # Mock vendor exists
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        
        # Mock ID generation
        id_manager_repo.get_next_id.return_value = 1
        
        # Mock transaction creation
        expected_transaction = PurchaseTransaction(
            transaction_id="PUR-000001",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        purchase_repo.create.return_value = expected_transaction
        purchase_repo.exists_by_transaction_id.return_value = False
        
        # Mock inventory item not found
        inventory_repo.find_by_id.return_value = None
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match=f"Inventory item with id {item_master_id} not found"):
            await use_case_instance.execute(
                vendor_id=vendor_id,
                transaction_date=transaction_date,
                items=items_data
            )
    
    @pytest.mark.asyncio
    async def test_create_transaction_with_items_duplicate_serial_numbers(self, use_case):
        """Test transaction creation with duplicate serial numbers."""
        (use_case_instance, purchase_repo, purchase_item_repo, vendor_repo, 
         inventory_repo, warehouse_repo, id_manager_repo) = use_case
        
        vendor_id = str(uuid4())
        item_master_id = str(uuid4())
        transaction_date = date.today()
        
        items_data = [
            {
                "item_master_id": item_master_id,
                "quantity": 1,
                "unit_price": "100.00",
                "serial_number": ["SN001"]
            }
        ]
        
        # Mock vendor exists
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        
        # Mock ID generation
        id_manager_repo.get_next_id.return_value = 1
        
        # Mock transaction creation
        expected_transaction = PurchaseTransaction(
            transaction_id="PUR-000001",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        purchase_repo.create.return_value = expected_transaction
        purchase_repo.exists_by_transaction_id.return_value = False
        
        # Mock inventory item exists
        mock_inventory_item = MagicMock()
        mock_inventory_item.tracking_type = "INDIVIDUAL"
        inventory_repo.find_by_id.return_value = mock_inventory_item
        
        # Mock serial numbers not unique
        purchase_item_repo.validate_serial_numbers_unique.return_value = False
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match="One or more serial numbers already exist"):
            await use_case_instance.execute(
                vendor_id=vendor_id,
                transaction_date=transaction_date,
                items=items_data
            )


class TestUpdatePurchaseTransactionUseCase:
    """Test update purchase transaction use case."""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories."""
        purchase_repository = AsyncMock()
        vendor_repository = AsyncMock()
        return purchase_repository, vendor_repository
    
    @pytest.fixture
    def use_case(self, mock_repositories):
        """Create use case with mocked dependencies."""
        purchase_repo, vendor_repo = mock_repositories
        return UpdatePurchaseTransactionUseCase(
            purchase_repository=purchase_repo,
            vendor_repository=vendor_repo
        ), purchase_repo, vendor_repo
    
    @pytest.mark.asyncio
    async def test_update_transaction_success(self, use_case):
        """Test successful transaction update."""
        use_case_instance, purchase_repo, vendor_repo = use_case
        
        # Setup test data
        transaction_id = str(uuid4())
        new_vendor_id = uuid4()
        new_transaction_date = date.today()
        new_remarks = "Updated remarks"
        
        # Mock existing transaction
        existing_transaction = PurchaseTransaction(
            entity_id=transaction_id,
            transaction_id="PUR-001",
            transaction_date=date(2024, 1, 1),
            vendor_id=uuid4(),
            remarks="Old remarks"
        )
        purchase_repo.get_by_id.return_value = existing_transaction
        
        # Mock new vendor exists
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        
        # Mock update
        updated_transaction = PurchaseTransaction(
            entity_id=transaction_id,
            transaction_id="PUR-001",
            transaction_date=new_transaction_date,
            vendor_id=new_vendor_id,
            remarks=new_remarks
        )
        purchase_repo.update.return_value = updated_transaction
        
        # Execute use case
        result = await use_case_instance.execute(
            transaction_id=transaction_id,
            vendor_id=new_vendor_id,
            transaction_date=new_transaction_date,
            remarks=new_remarks
        )
        
        # Verify interactions
        purchase_repo.get_by_id.assert_called_once_with(transaction_id)
        vendor_repo.find_by_id.assert_called_once_with(new_vendor_id)
        purchase_repo.update.assert_called_once()
        
        # Verify result
        assert result.transaction_date == new_transaction_date
        assert result.vendor_id == new_vendor_id
        assert result.remarks == new_remarks
    
    @pytest.mark.asyncio
    async def test_update_transaction_not_found(self, use_case):
        """Test update of non-existent transaction."""
        use_case_instance, purchase_repo, vendor_repo = use_case
        
        transaction_id = str(uuid4())
        
        # Mock transaction not found
        purchase_repo.get_by_id.return_value = None
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match=f"Purchase transaction with id {transaction_id} not found"):
            await use_case_instance.execute(transaction_id=transaction_id)
        
        # Verify no update was attempted
        purchase_repo.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_transaction_not_editable(self, use_case):
        """Test update of non-editable transaction."""
        use_case_instance, purchase_repo, vendor_repo = use_case
        
        transaction_id = str(uuid4())
        
        # Mock existing transaction that's not editable
        existing_transaction = MagicMock()
        existing_transaction.is_editable.return_value = False
        purchase_repo.get_by_id.return_value = existing_transaction
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match="Cannot edit transaction"):
            await use_case_instance.execute(transaction_id=transaction_id)
        
        # Verify no update was attempted
        purchase_repo.update.assert_not_called()


class TestDeletePurchaseTransactionUseCase:
    """Test delete purchase transaction use case."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mocked dependencies."""
        return DeletePurchaseTransactionUseCase(
            purchase_repository=mock_repository
        ), mock_repository
    
    @pytest.mark.asyncio
    async def test_delete_transaction_success(self, use_case):
        """Test successful transaction deletion."""
        use_case_instance, purchase_repo = use_case
        
        transaction_id = str(uuid4())
        
        # Mock existing transaction
        existing_transaction = MagicMock()
        existing_transaction.is_cancellable.return_value = True
        purchase_repo.get_by_id.return_value = existing_transaction
        
        # Mock successful deletion
        purchase_repo.delete.return_value = True
        
        # Execute use case
        result = await use_case_instance.execute(transaction_id)
        
        # Verify interactions
        purchase_repo.get_by_id.assert_called_once_with(transaction_id)
        purchase_repo.delete.assert_called_once_with(transaction_id)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_transaction_not_found(self, use_case):
        """Test deletion of non-existent transaction."""
        use_case_instance, purchase_repo = use_case
        
        transaction_id = str(uuid4())
        
        # Mock transaction not found
        purchase_repo.get_by_id.return_value = None
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match=f"Purchase transaction with id {transaction_id} not found"):
            await use_case_instance.execute(transaction_id)
        
        # Verify no deletion was attempted
        purchase_repo.delete.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_transaction_not_cancellable(self, use_case):
        """Test deletion of non-cancellable transaction."""
        use_case_instance, purchase_repo = use_case
        
        transaction_id = str(uuid4())
        
        # Mock existing transaction that's not cancellable
        existing_transaction = MagicMock()
        existing_transaction.is_cancellable.return_value = False
        purchase_repo.get_by_id.return_value = existing_transaction
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match="Cannot delete completed transaction"):
            await use_case_instance.execute(transaction_id)
        
        # Verify no deletion was attempted
        purchase_repo.delete.assert_not_called()


class TestListPurchaseTransactionsUseCase:
    """Test list purchase transactions use case."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        return AsyncMock()
    
    @pytest.fixture
    def use_case(self, mock_repository):
        """Create use case with mocked dependencies."""
        return ListPurchaseTransactionsUseCase(
            purchase_repository=mock_repository
        ), mock_repository
    
    @pytest.mark.asyncio
    async def test_list_transactions_success(self, use_case):
        """Test successful transaction listing."""
        use_case_instance, purchase_repo = use_case
        
        # Setup test data
        vendor_id = str(uuid4())
        date_from = date(2024, 1, 1)
        date_to = date(2024, 12, 31)
        
        # Mock transactions
        mock_transactions = [
            MagicMock(),
            MagicMock(),
            MagicMock()
        ]
        purchase_repo.list.return_value = mock_transactions
        purchase_repo.count.return_value = 25
        
        # Execute use case
        result = await use_case_instance.execute(
            page=2,
            page_size=10,
            vendor_id=vendor_id,
            date_from=date_from,
            date_to=date_to,
            sort_by="transaction_date",
            sort_desc=False
        )
        
        # Verify interactions
        expected_skip = 10  # (page - 1) * page_size
        expected_filters = {
            "vendor_id": vendor_id,
            "date_from": date_from,
            "date_to": date_to
        }
        
        purchase_repo.list.assert_called_once_with(
            skip=expected_skip,
            limit=10,
            filters=expected_filters,
            sort_by="transaction_date",
            sort_desc=False
        )
        purchase_repo.count.assert_called_once_with(expected_filters)
        
        # Verify result
        assert result["transactions"] == mock_transactions
        assert result["total"] == 25
        assert result["page"] == 2
        assert result["page_size"] == 10
        assert result["total_pages"] == 3  # ceil(25 / 10)
    
    @pytest.mark.asyncio
    async def test_list_transactions_no_filters(self, use_case):
        """Test listing transactions without filters."""
        use_case_instance, purchase_repo = use_case
        
        # Mock empty results
        purchase_repo.list.return_value = []
        purchase_repo.count.return_value = 0
        
        # Execute use case with defaults
        result = await use_case_instance.execute()
        
        # Verify interactions
        purchase_repo.list.assert_called_once_with(
            skip=0,
            limit=50,
            filters={},
            sort_by=None,
            sort_desc=True
        )
        purchase_repo.count.assert_called_once_with({})
        
        # Verify result
        assert result["transactions"] == []
        assert result["total"] == 0
        assert result["page"] == 1
        assert result["page_size"] == 50
        assert result["total_pages"] == 0


class TestPurchaseTransactionService:
    """Test purchase transaction service integration."""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories."""
        purchase_repository = AsyncMock()
        purchase_item_repository = AsyncMock()
        vendor_repository = AsyncMock()
        inventory_repository = AsyncMock()
        warehouse_repository = AsyncMock()
        id_manager_repository = AsyncMock()
        return (purchase_repository, purchase_item_repository, vendor_repository,
                inventory_repository, warehouse_repository, id_manager_repository)
    
    @pytest.fixture
    def service(self, mock_repositories):
        """Create service with mocked dependencies."""
        (purchase_repo, purchase_item_repo, vendor_repo,
         inventory_repo, warehouse_repo, id_manager_repo) = mock_repositories
        
        return PurchaseTransactionService(
            purchase_repository=purchase_repo,
            purchase_item_repository=purchase_item_repo,
            vendor_repository=vendor_repo,
            inventory_repository=inventory_repo,
            warehouse_repository=warehouse_repo,
            id_manager_repository=id_manager_repo
        ), purchase_repo, purchase_item_repo, vendor_repo, inventory_repo, warehouse_repo, id_manager_repo
    
    @pytest.mark.asyncio
    async def test_create_transaction_service_integration(self, service):
        """Test service-level transaction creation."""
        (service_instance, purchase_repo, purchase_item_repo, vendor_repo,
         inventory_repo, warehouse_repo, id_manager_repo) = service
        
        # Setup test data
        vendor_id = str(uuid4())
        transaction_date = date.today()
        created_by = "test_user"
        
        # Mock dependencies
        mock_vendor = MagicMock()
        vendor_repo.find_by_id.return_value = mock_vendor
        id_manager_repo.get_next_id.return_value = 1
        purchase_repo.exists_by_transaction_id.return_value = False
        
        expected_transaction = PurchaseTransaction(
            transaction_id="PUR-000001",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            created_by=created_by
        )
        purchase_repo.create.return_value = expected_transaction
        
        # Execute service method
        result = await service_instance.create_transaction(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            created_by=created_by
        )
        
        # Verify result
        assert result.transaction_id == "PUR-000001"
        assert result.vendor_id == vendor_id
        assert result.created_by == created_by
    
    @pytest.mark.asyncio
    async def test_get_transaction_with_items_service_integration(self, service):
        """Test service-level get transaction with items."""
        (service_instance, purchase_repo, purchase_item_repo, vendor_repo,
         inventory_repo, warehouse_repo, id_manager_repo) = service
        
        transaction_id = str(uuid4())
        
        # Mock transaction
        mock_transaction = MagicMock()
        purchase_repo.get_by_id.return_value = mock_transaction
        
        # Mock items result
        mock_items = [MagicMock(), MagicMock()]
        items_result = {
            "items": mock_items,
            "total": 2,
            "page": 1,
            "page_size": 1000,
            "total_pages": 1
        }
        purchase_item_repo.get_by_transaction_id.return_value = mock_items
        purchase_item_repo.count_by_transaction_id.return_value = 2
        
        # Mock summary
        mock_summary = {"total_items": 2, "total_amount": 500.00}
        purchase_item_repo.get_transaction_item_summary.return_value = mock_summary
        
        # Execute service method
        result = await service_instance.get_transaction_with_items(transaction_id)
        
        # Verify interactions
        purchase_repo.get_by_id.assert_called_once_with(transaction_id)
        purchase_item_repo.get_transaction_item_summary.assert_called_once_with(transaction_id)
        
        # Verify result structure
        assert result["transaction"] == mock_transaction
        assert result["items"] == mock_items
        assert result["item_summary"] == mock_summary
    
    @pytest.mark.asyncio
    async def test_get_transaction_with_items_not_found(self, service):
        """Test service-level get transaction with items when transaction not found."""
        (service_instance, purchase_repo, purchase_item_repo, vendor_repo,
         inventory_repo, warehouse_repo, id_manager_repo) = service
        
        transaction_id = str(uuid4())
        
        # Mock transaction not found
        purchase_repo.get_by_id.return_value = None
        
        # Execute service method
        result = await service_instance.get_transaction_with_items(transaction_id)
        
        # Verify result
        assert result is None
        
        # Verify no items lookup was attempted
        purchase_item_repo.get_by_transaction_id.assert_not_called()


class TestPurchaseTransactionItemUseCases:
    """Test purchase transaction item use cases."""
    
    @pytest.fixture
    def mock_repositories(self):
        """Create mock repositories."""
        purchase_repository = AsyncMock()
        purchase_item_repository = AsyncMock()
        inventory_repository = AsyncMock()
        warehouse_repository = AsyncMock()
        return purchase_repository, purchase_item_repository, inventory_repository, warehouse_repository
    
    @pytest.fixture
    def create_item_use_case(self, mock_repositories):
        """Create item use case with mocked dependencies."""
        purchase_repo, purchase_item_repo, inventory_repo, warehouse_repo = mock_repositories
        return CreatePurchaseTransactionItemUseCase(
            purchase_repository=purchase_repo,
            purchase_item_repository=purchase_item_repo,
            inventory_repository=inventory_repo,
            warehouse_repository=warehouse_repo
        ), purchase_repo, purchase_item_repo, inventory_repo, warehouse_repo
    
    @pytest.mark.asyncio
    async def test_create_item_success(self, create_item_use_case):
        """Test successful item creation."""
        (use_case_instance, purchase_repo, purchase_item_repo, 
         inventory_repo, warehouse_repo) = create_item_use_case
        
        # Setup test data
        transaction_id = str(uuid4())
        item_master_id = str(uuid4())
        warehouse_id = str(uuid4())
        
        # Mock transaction exists and can add items
        mock_transaction = MagicMock()
        mock_transaction.can_add_items.return_value = True
        purchase_repo.get_by_id.return_value = mock_transaction
        
        # Mock inventory item exists
        mock_inventory_item = MagicMock()
        mock_inventory_item.tracking_type = "BULK"
        inventory_repo.find_by_id.return_value = mock_inventory_item
        
        # Mock warehouse exists
        mock_warehouse = MagicMock()
        warehouse_repo.find_by_id.return_value = mock_warehouse
        
        # Mock serial number validation
        purchase_item_repo.validate_serial_numbers_unique.return_value = True
        
        # Mock item creation
        expected_item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=item_master_id,
            quantity=2,
            unit_price=Decimal("100.00"),
            warehouse_id=warehouse_id
        )
        purchase_item_repo.create.return_value = expected_item
        
        # Mock summary for total update
        mock_summary = {"total_amount": 200.00}
        purchase_item_repo.get_transaction_item_summary.return_value = mock_summary
        
        # Mock transaction totals update
        updated_transaction = MagicMock()
        purchase_repo.update_totals.return_value = updated_transaction
        
        # Execute use case
        result = await use_case_instance.execute(
            transaction_id=transaction_id,
            item_master_id=item_master_id,
            quantity=2,
            unit_price=Decimal("100.00"),
            warehouse_id=warehouse_id
        )
        
        # Verify interactions
        purchase_repo.get_by_id.assert_called_once_with(transaction_id)
        inventory_repo.find_by_id.assert_called_once_with(item_master_id)
        warehouse_repo.find_by_id.assert_called_once_with(warehouse_id)
        purchase_item_repo.create.assert_called_once()
        purchase_item_repo.get_transaction_item_summary.assert_called_once_with(transaction_id)
        purchase_repo.update_totals.assert_called_once()
        
        # Verify result
        assert result.transaction_id == transaction_id
        assert result.inventory_item_id == item_master_id
        assert result.quantity == 2
        assert result.unit_price == Decimal("100.00")
    
    @pytest.mark.asyncio
    async def test_create_item_transaction_cannot_add_items(self, create_item_use_case):
        """Test item creation when transaction cannot add items."""
        (use_case_instance, purchase_repo, purchase_item_repo, 
         inventory_repo, warehouse_repo) = create_item_use_case
        
        transaction_id = str(uuid4())
        item_master_id = str(uuid4())
        
        # Mock transaction exists but cannot add items
        mock_transaction = MagicMock()
        mock_transaction.can_add_items.return_value = False
        purchase_repo.get_by_id.return_value = mock_transaction
        
        # Execute use case and expect error
        with pytest.raises(ValueError, match="Cannot add items to transaction"):
            await use_case_instance.execute(
                transaction_id=transaction_id,
                item_master_id=item_master_id,
                quantity=1,
                unit_price=Decimal("100.00")
            )
        
        # Verify no item was created
        purchase_item_repo.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_bulk_create_items_success(self, mock_repositories):
        """Test successful bulk item creation."""
        purchase_repo, purchase_item_repo, inventory_repo, warehouse_repo = mock_repositories
        
        use_case = BulkCreatePurchaseTransactionItemsUseCase(
            purchase_repository=purchase_repo,
            purchase_item_repository=purchase_item_repo,
            inventory_repository=inventory_repo,
            warehouse_repository=warehouse_repo
        )
        
        # Setup test data
        transaction_id = str(uuid4())
        item_master_id1 = uuid4()
        item_master_id2 = uuid4()
        
        items_data = [
            {
                "item_master_id": item_master_id1,
                "quantity": 1,
                "unit_price": "100.00"
            },
            {
                "item_master_id": item_master_id2,
                "quantity": 2,
                "unit_price": "150.00"
            }
        ]
        
        # Mock transaction exists and can add items
        mock_transaction = MagicMock()
        mock_transaction.can_add_items.return_value = True
        purchase_repo.get_by_id.return_value = mock_transaction
        
        # Mock inventory items exist
        mock_inventory_item1 = MagicMock()
        mock_inventory_item1.tracking_type = "BULK"
        mock_inventory_item2 = MagicMock()
        mock_inventory_item2.tracking_type = "BULK"
        inventory_repo.find_by_id.side_effect = [mock_inventory_item1, mock_inventory_item2]
        
        # Mock serial number validation
        purchase_item_repo.validate_serial_numbers_unique.return_value = True
        
        # Mock bulk creation
        expected_items = [
            MagicMock(),
            MagicMock()
        ]
        purchase_item_repo.bulk_create.return_value = expected_items
        
        # Mock summary for total update
        mock_summary = {"total_amount": 400.00}
        purchase_item_repo.get_transaction_item_summary.return_value = mock_summary
        
        # Mock transaction totals update
        updated_transaction = MagicMock()
        purchase_repo.update_totals.return_value = updated_transaction
        
        # Execute use case
        result = await use_case.execute(
            transaction_id=transaction_id,
            items=items_data,
            created_by="test_user"
        )
        
        # Verify interactions
        purchase_repo.get_by_id.assert_called_once_with(transaction_id)
        assert inventory_repo.find_by_id.call_count == 2
        purchase_item_repo.bulk_create.assert_called_once()
        purchase_repo.update_totals.assert_called_once()
        
        # Verify result
        assert result == expected_items