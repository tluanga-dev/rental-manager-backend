"""
Unit tests for Purchase Transaction Infrastructure Layer.

Tests repository implementations with mocked database sessions:
- SQLAlchemyPurchaseTransactionRepository
- SQLAlchemyPurchaseTransactionItemRepository
- Database model conversions
- Query building and filtering
- Error handling
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4
from typing import List, Dict, Any

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem
from src.infrastructure.repositories.purchase_transaction_repository_impl import SQLAlchemyPurchaseTransactionRepository
from src.infrastructure.repositories.purchase_transaction_item_repository_impl import SQLAlchemyPurchaseTransactionItemRepository
from src.infrastructure.database.models import PurchaseTransactionModel, PurchaseTransactionItemModel


def create_mock_transaction_model(**overrides):
    """Helper function to create a properly structured mock transaction model."""
    defaults = {
        'id': str(uuid4()),
        'transaction_id': 'PUR-001',
        'transaction_date': date.today(),
        'vendor_id': str(uuid4()),
        'total_amount': 100.00,
        'grand_total': 105.00,
        'purchase_order_number': 'PO-001',
        'remarks': 'Test transaction',
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
        'created_by': 'test_user',
        'is_active': True
    }
    defaults.update(overrides)
    
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


def create_mock_transaction_item_model(**overrides):
    """Helper function to create a properly structured mock transaction item model."""
    defaults = {
        'id': str(uuid4()),
        'transaction_id': str(uuid4()),
        'inventory_item_id': str(uuid4()),
        'warehouse_id': str(uuid4()),
        'quantity': 1,
        'unit_price': 100.00,
        'discount': 0.00,
        'tax_amount': 0.00,
        'total_price': 100.00,
        'serial_number': [],
        'remarks': None,
        'warranty_period_type': None,
        'warranty_period': None,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc),
        'created_by': 'test_user',
        'is_active': True
    }
    defaults.update(overrides)
    
    mock = MagicMock()
    for key, value in defaults.items():
        setattr(mock, key, value)
    return mock


class TestSQLAlchemyPurchaseTransactionRepository:
    """Test SQLAlchemy purchase transaction repository implementation."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_session):
        """Create repository with mocked session."""
        return SQLAlchemyPurchaseTransactionRepository(mock_session), mock_session
    
    @pytest.mark.asyncio
    async def test_create_transaction(self, repository):
        """Test creating a new transaction."""
        repo, mock_session = repository
        
        # Setup test data
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-001",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            total_amount=Decimal("500.00"),
            grand_total=Decimal("525.00"),
            purchase_order_number="PO-001",
            remarks="Test transaction"
        )
        
        # Mock database operations
        mock_model = MagicMock()
        mock_model.id = transaction.id
        mock_model.transaction_id = "PUR-001"
        mock_model.transaction_date = transaction_date
        mock_model.vendor_id = vendor_id
        mock_model.total_amount = 500.00
        mock_model.grand_total = 525.00
        mock_model.purchase_order_number = "PO-001"
        mock_model.remarks = "Test transaction"
        mock_model.created_at = transaction.created_at
        mock_model.updated_at = transaction.updated_at
        mock_model.created_by = transaction.created_by
        mock_model.is_active = True
        
        # Execute repository method
        result = await repo.create(transaction)
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Verify result
        assert isinstance(result, PurchaseTransaction)
        assert result.transaction_id == "PUR-001"
        assert result.vendor_id == vendor_id
        assert result.total_amount == Decimal("500.00")
    
    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository):
        """Test retrieving transaction by ID when found."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        
        # Mock database model
        mock_model = MagicMock()
        mock_model.id = transaction_id
        mock_model.transaction_id = "PUR-002"
        mock_model.transaction_date = date.today()
        mock_model.vendor_id = str(uuid4())
        mock_model.total_amount = 300.00
        mock_model.grand_total = 315.00
        mock_model.purchase_order_number = None
        mock_model.remarks = None
        mock_model.created_at = datetime.now(timezone.utc)
        mock_model.updated_at = datetime.now(timezone.utc)
        mock_model.created_by = "test_user"
        mock_model.is_active = True
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.get_by_id(transaction_id)
        
        # Verify database query
        mock_session.query.assert_called_once_with(PurchaseTransactionModel)
        mock_query.filter.assert_called_once()
        
        # Verify result
        assert isinstance(result, PurchaseTransaction)
        assert result.id == transaction_id
        assert result.transaction_id == "PUR-002"
        assert result.total_amount == Decimal("300.00")
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test retrieving transaction by ID when not found."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        
        # Mock query returning None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.get_by_id(transaction_id)
        
        # Verify result
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_transaction_id(self, repository):
        """Test retrieving transaction by transaction ID."""
        repo, mock_session = repository
        
        transaction_id = "PUR-003"
        
        # Mock database model
        mock_model = MagicMock()
        mock_model.id = uuid4()
        mock_model.transaction_id = transaction_id
        mock_model.transaction_date = date.today()
        mock_model.vendor_id = str(uuid4())
        mock_model.total_amount = 750.00
        mock_model.grand_total = 787.50
        mock_model.purchase_order_number = "PO-002"
        mock_model.remarks = "Test by transaction ID"
        mock_model.created_at = datetime.now(timezone.utc)
        mock_model.updated_at = datetime.now(timezone.utc)
        mock_model.created_by = "test_user"
        mock_model.is_active = True
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.get_by_transaction_id(transaction_id)
        
        # Verify result
        assert isinstance(result, PurchaseTransaction)
        assert result.transaction_id == transaction_id
        assert result.purchase_order_number == "PO-002"
    
    @pytest.mark.asyncio
    async def test_update_transaction(self, repository):
        """Test updating an existing transaction."""
        repo, mock_session = repository
        
        # Setup test data
        transaction_id = str(uuid4())
        vendor_id = str(uuid4())
        updated_transaction = PurchaseTransaction(
            entity_id=transaction_id,
            transaction_id="PUR-004",
            transaction_date=date.today(),
            vendor_id=vendor_id,
            total_amount=Decimal("1000.00"),
            grand_total=Decimal("1050.00"),
            purchase_order_number="PO-003",
            remarks="Updated transaction"
        )
        
        # Mock existing model
        mock_model = MagicMock()
        mock_model.id = transaction_id
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.update(updated_transaction)
        
        # Verify database operations
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_model)
        
        # Verify model was updated
        assert mock_model.transaction_id == "PUR-004"
        assert mock_model.vendor_id == vendor_id
        assert mock_model.total_amount == 1000.00
        assert mock_model.grand_total == 1050.00
        assert mock_model.purchase_order_number == "PO-003"
        assert mock_model.remarks == "Updated transaction"
    
    @pytest.mark.asyncio
    async def test_update_transaction_not_found(self, repository):
        """Test updating non-existent transaction."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        transaction = PurchaseTransaction(
            entity_id=transaction_id,
            transaction_id="PUR-404",
            transaction_date=date.today(),
            vendor_id=uuid4()
        )
        
        # Mock query returning None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Execute repository method and expect error
        with pytest.raises(ValueError, match=f"Purchase transaction with id {transaction_id} not found"):
            await repo.update(transaction)
    
    @pytest.mark.asyncio
    async def test_delete_transaction(self, repository):
        """Test soft deleting a transaction."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        
        # Mock existing model
        mock_model = MagicMock()
        mock_model.id = transaction_id
        mock_model.is_active = True
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.delete(transaction_id)
        
        # Verify database operations
        mock_session.commit.assert_called_once()
        
        # Verify model was soft deleted
        assert mock_model.is_active is False
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_transaction_not_found(self, repository):
        """Test deleting non-existent transaction."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        
        # Mock query returning None
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.delete(transaction_id)
        
        # Verify result
        assert result is False
        mock_session.commit.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_list_transactions_with_filters(self, repository):
        """Test listing transactions with filters."""
        repo, mock_session = repository
        
        # Setup filter data
        vendor_id = str(uuid4())
        date_from = date(2024, 1, 1)
        date_to = date(2024, 12, 31)
        filters = {
            "vendor_id": vendor_id,
            "date_from": date_from,
            "date_to": date_to,
            "purchase_order_number": "PO-"
        }
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        
        # Mock filter chain
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock results with proper attributes
        mock_models = []
        for i in range(3):
            mock_model = MagicMock()
            mock_model.id = uuid4()
            mock_model.transaction_id = f"PUR-{i+1:03d}"
            mock_model.transaction_date = date.today()
            mock_model.vendor_id = vendor_id
            mock_model.total_amount = 100.00 * (i + 1)
            mock_model.grand_total = 105.00 * (i + 1)
            mock_model.purchase_order_number = f"PO-{i+1:03d}"
            mock_model.remarks = f"Test transaction {i+1}"
            mock_model.created_at = datetime.now(timezone.utc)
            mock_model.updated_at = datetime.now(timezone.utc)
            mock_model.created_by = "test_user"
            mock_model.is_active = True
            mock_models.append(mock_model)
        mock_query.all.return_value = mock_models
        
        # Execute repository method
        result = await repo.list(
            skip=10,
            limit=20,
            filters=filters,
            sort_by="transaction_date",
            sort_desc=False
        )
        
        # Verify query building
        mock_session.query.assert_called_once_with(PurchaseTransactionModel)
        assert mock_query.filter.call_count >= 5  # Multiple filter conditions
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(10)
        mock_query.limit.assert_called_once_with(20)
        
        # Verify result is list of entities
        assert len(result) == 3
        assert all(isinstance(t, PurchaseTransaction) for t in result)
    
    @pytest.mark.asyncio
    async def test_list_transactions_no_filters(self, repository):
        """Test listing transactions without filters."""
        repo, mock_session = repository
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        
        # Mock filter chain
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        
        # Execute repository method
        result = await repo.list()
        
        # Verify default parameters
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(100)
        
        # Verify result
        assert result == []
    
    @pytest.mark.asyncio
    async def test_count_transactions_with_filters(self, repository):
        """Test counting transactions with filters."""
        repo, mock_session = repository
        
        vendor_id = str(uuid4())
        filters = {"vendor_id": vendor_id}
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 42
        
        # Execute repository method
        result = await repo.count(filters)
        
        # Verify query building
        mock_session.query.assert_called_once_with(PurchaseTransactionModel)
        mock_query.filter.assert_called()
        mock_query.count.assert_called_once()
        
        # Verify result
        assert result == 42
    
    @pytest.mark.asyncio
    async def test_get_by_vendor(self, repository):
        """Test getting transactions by vendor."""
        repo, mock_session = repository
        
        vendor_id = str(uuid4())
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock results with proper attributes
        mock_models = []
        for i in range(2):
            mock_model = MagicMock()
            mock_model.id = uuid4()
            mock_model.transaction_id = f"PUR-VENDOR-{i+1:03d}"
            mock_model.transaction_date = date.today()
            mock_model.vendor_id = vendor_id
            mock_model.total_amount = 200.00 * (i + 1)
            mock_model.grand_total = 210.00 * (i + 1)
            mock_model.purchase_order_number = f"PO-VENDOR-{i+1:03d}"
            mock_model.remarks = f"Vendor transaction {i+1}"
            mock_model.created_at = datetime.now(timezone.utc)
            mock_model.updated_at = datetime.now(timezone.utc)
            mock_model.created_by = "test_user"
            mock_model.is_active = True
            mock_models.append(mock_model)
        mock_query.all.return_value = mock_models
        
        # Execute repository method
        result = await repo.get_by_vendor(
            vendor_id=vendor_id,
            skip=5,
            limit=15
        )
        
        # Verify query building
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called()
        mock_query.offset.assert_called_once_with(5)
        mock_query.limit.assert_called_once_with(15)
        
        # Verify result
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_by_purchase_order_number(self, repository):
        """Test getting transaction by purchase order number."""
        repo, mock_session = repository
        
        po_number = "PO-12345"
        
        # Mock database model
        mock_model = create_mock_transaction_model(purchase_order_number=po_number)
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.get_by_purchase_order_number(po_number)
        
        # Verify result
        assert isinstance(result, PurchaseTransaction)
    
    @pytest.mark.asyncio
    async def test_search_transactions(self, repository):
        """Test searching transactions by text query."""
        repo, mock_session = repository
        
        search_query = "test"
        vendor_id = str(uuid4())
        filters = {"vendor_id": vendor_id}
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [create_mock_transaction_model()]
        
        # Execute repository method
        result = await repo.search(search_query, filters)
        
        # Verify query building
        mock_session.query.assert_called_once_with(PurchaseTransactionModel)
        assert mock_query.filter.call_count >= 2  # Search conditions + additional filters
        mock_query.limit.assert_called_once_with(100)
        
        # Verify result
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_update_totals(self, repository):
        """Test updating transaction totals."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        total_amount = Decimal("750.00")
        grand_total = Decimal("787.50")
        
        # Mock existing model
        mock_model = MagicMock()
        mock_model.id = transaction_id
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.update_totals(transaction_id, total_amount, grand_total)
        
        # Verify database operations
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_model)
        
        # Verify totals were updated
        assert mock_model.total_amount == 750.00
        assert mock_model.grand_total == 787.50
        
        # Verify result
        assert isinstance(result, PurchaseTransaction)
    
    @pytest.mark.asyncio
    async def test_exists_by_transaction_id_exists(self, repository):
        """Test checking transaction ID existence when exists."""
        repo, mock_session = repository
        
        transaction_id = "PUR-EXISTS"
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = MagicMock()
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.exists_by_transaction_id(transaction_id)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_exists_by_transaction_id_not_exists(self, repository):
        """Test checking transaction ID existence when doesn't exist."""
        repo, mock_session = repository
        
        transaction_id = "PUR-NOTEXISTS"
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.exists_by_transaction_id(transaction_id)
        
        # Verify result
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_statistics(self, repository):
        """Test getting transaction statistics."""
        repo, mock_session = repository
        
        # Mock query chain for total stats
        mock_total_query = MagicMock()
        mock_total_query.filter.return_value = mock_total_query
        mock_total_query.with_entities.return_value.scalar.return_value = 15000.00
        mock_total_query.count.return_value = 150
        
        # Mock query chain for recent stats
        mock_recent_query = MagicMock()
        mock_recent_query.filter.return_value = mock_recent_query
        mock_recent_query.with_entities.return_value.scalar.return_value = 5000.00
        mock_recent_query.count.return_value = 50
        
        mock_session.query.return_value = mock_total_query
        
        # Execute repository method
        with patch('src.infrastructure.repositories.purchase_transaction_repository_impl.date') as mock_date:
            mock_date.today.return_value.replace.return_value = date(2024, 6, 1)
            result = await repo.get_statistics()
        
        # Verify result structure
        assert "total_amount" in result
        assert "total_transactions" in result
        assert "recent_amount" in result
        assert "recent_transactions" in result
        assert result["total_amount"] == 15000.00
        assert result["total_transactions"] == 150
    
    @pytest.mark.asyncio
    async def test_get_purchase_summary(self, repository):
        """Test getting purchase summary for date range."""
        repo, mock_session = repository
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 100
        
        # Mock aggregation result
        mock_totals = MagicMock()
        mock_totals.total_amount = 25000.00
        mock_totals.grand_total = 26250.00
        mock_totals.avg_amount = 262.50
        mock_query.with_entities.return_value.first.return_value = mock_totals
        
        # Execute repository method
        result = await repo.get_purchase_summary(start_date, end_date)
        
        # Verify result structure
        assert "period" in result
        assert "total_transactions" in result
        assert "total_amount" in result
        assert "grand_total" in result
        assert "average_amount" in result
        assert result["period"]["start_date"] == "2024-01-01"
        assert result["period"]["end_date"] == "2024-12-31"
        assert result["total_transactions"] == 100
        assert result["total_amount"] == 25000.00
        assert result["grand_total"] == 26250.00
        assert result["average_amount"] == 262.50
    
    def test_entity_to_model_conversion(self, repository):
        """Test converting entity to database model."""
        repo, mock_session = repository
        
        # Setup test entity
        vendor_id = str(uuid4())
        transaction = PurchaseTransaction(
            transaction_id="PUR-CONVERT",
            transaction_date=date.today(),
            vendor_id=vendor_id,
            total_amount=Decimal("500.00"),
            grand_total=Decimal("525.00"),
            purchase_order_number="PO-CONVERT",
            remarks="Test conversion"
        )
        
        # Convert entity to model
        model = repo._entity_to_model(transaction)
        
        # Verify conversion
        assert model.id == transaction.id
        assert model.transaction_id == "PUR-CONVERT"
        assert model.transaction_date == transaction.transaction_date
        assert model.vendor_id == vendor_id
        assert model.total_amount == 500.00
        assert model.grand_total == 525.00
        assert model.purchase_order_number == "PO-CONVERT"
        assert model.remarks == "Test conversion"
        assert model.created_at == transaction.created_at
        assert model.updated_at == transaction.updated_at
        assert model.created_by == transaction.created_by
        assert model.is_active == transaction.is_active
    
    def test_model_to_entity_conversion(self, repository):
        """Test converting database model to entity."""
        repo, mock_session = repository
        
        # Setup test model
        model_id = uuid4()
        vendor_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        
        model = MagicMock()
        model.id = model_id
        model.transaction_id = "PUR-CONVERT"
        model.transaction_date = date.today()
        model.vendor_id = vendor_id
        model.total_amount = 750.00
        model.grand_total = 787.50
        model.purchase_order_number = "PO-CONVERT"
        model.remarks = "Test conversion"
        model.created_at = created_at
        model.updated_at = created_at
        model.created_by = "test_user"
        model.is_active = True
        
        # Convert model to entity
        entity = repo._model_to_entity(model)
        
        # Verify conversion
        assert entity.id == model_id
        assert entity.transaction_id == "PUR-CONVERT"
        assert entity.transaction_date == model.transaction_date
        assert entity.vendor_id == vendor_id
        assert entity.total_amount == Decimal("750.00")
        assert entity.grand_total == Decimal("787.50")
        assert entity.purchase_order_number == "PO-CONVERT"
        assert entity.remarks == "Test conversion"
        assert entity.created_at == created_at
        assert entity.updated_at == created_at
        assert entity.created_by == "test_user"
        assert entity.is_active is True
    
    def test_model_to_entity_conversion_none(self, repository):
        """Test converting None model returns None."""
        repo, mock_session = repository
        
        # Convert None model
        entity = repo._model_to_entity(None)
        
        # Verify result
        assert entity is None


class TestSQLAlchemyPurchaseTransactionItemRepository:
    """Test SQLAlchemy purchase transaction item repository implementation."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def repository(self, mock_session):
        """Create repository with mocked session."""
        return SQLAlchemyPurchaseTransactionItemRepository(mock_session), mock_session
    
    @pytest.mark.asyncio
    async def test_create_item(self, repository):
        """Test creating a new item."""
        repo, mock_session = repository
        
        # Setup test data
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("100.00"),
            discount=Decimal("30.00"),
            tax_amount=Decimal("20.00"),
            serial_number=["SN001", "SN002", "SN003"]
        )
        
        # Mock database operations
        mock_model = MagicMock()
        mock_model.id = item.id
        
        # Execute repository method
        result = await repo.create(item)
        
        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
        # Verify result
        assert isinstance(result, PurchaseTransactionItem)
    
    @pytest.mark.asyncio
    async def test_bulk_create_items(self, repository):
        """Test creating multiple items atomically."""
        repo, mock_session = repository
        
        # Setup test data
        transaction_id = str(uuid4())
        items = [
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=uuid4(),
                quantity=1,
                unit_price=Decimal("100.00")
            ),
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=uuid4(),
                quantity=2,
                unit_price=Decimal("150.00")
            )
        ]
        
        # Mock database operations
        mock_models = [MagicMock(), MagicMock()]
        
        # Execute repository method
        result = await repo.bulk_create(items)
        
        # Verify database operations
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_called_once()
        assert mock_session.refresh.call_count == 2
        
        # Verify result
        assert len(result) == 2
        assert all(isinstance(item, PurchaseTransactionItem) for item in result)
    
    @pytest.mark.asyncio
    async def test_get_by_transaction_id(self, repository):
        """Test getting items by transaction ID."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        
        # Mock results with proper attributes
        mock_models = [
            create_mock_transaction_item_model(transaction_id=transaction_id),
            create_mock_transaction_item_model(transaction_id=transaction_id)
        ]
        mock_query.all.return_value = mock_models
        
        # Execute repository method
        result = await repo.get_by_transaction_id(
            transaction_id=transaction_id,
            skip=5,
            limit=10
        )
        
        # Verify query building
        mock_session.query.assert_called_once_with(PurchaseTransactionItemModel)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called()
        mock_query.offset.assert_called_once_with(5)
        mock_query.limit.assert_called_once_with(10)
        
        # Verify result
        assert len(result) == 2
    
    @pytest.mark.asyncio
    async def test_get_by_serial_number(self, repository):
        """Test getting item by serial number."""
        repo, mock_session = repository
        
        serial_number = "SN12345"
        
        # Mock database model with proper attributes
        mock_model = create_mock_transaction_item_model(serial_number=[serial_number])
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.get_by_serial_number(serial_number)
        
        # Verify result
        assert isinstance(result, PurchaseTransactionItem)
    
    @pytest.mark.asyncio
    async def test_check_serial_number_exists_true(self, repository):
        """Test checking serial number existence when exists."""
        repo, mock_session = repository
        
        serial_number = "SN_EXISTS"
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = MagicMock()
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.check_serial_number_exists(serial_number)
        
        # Verify result
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_serial_number_exists_false(self, repository):
        """Test checking serial number existence when doesn't exist."""
        repo, mock_session = repository
        
        serial_number = "SN_NOT_EXISTS"
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.check_serial_number_exists(serial_number)
        
        # Verify result
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_serial_numbers_unique_all_unique(self, repository):
        """Test validating serial numbers when all are unique."""
        repo, mock_session = repository
        
        serial_numbers = ["SN001", "SN002", "SN003"]
        
        # Mock each serial number check to return False (not existing)
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.validate_serial_numbers_unique(serial_numbers)
        
        # Verify result
        assert result is True
        # Verify all serial numbers were checked
        assert mock_session.query.call_count == 3
    
    @pytest.mark.asyncio
    async def test_validate_serial_numbers_unique_has_duplicate(self, repository):
        """Test validating serial numbers when one exists."""
        repo, mock_session = repository
        
        serial_numbers = ["SN001", "SN002", "SN_EXISTS"]
        
        # Mock first two checks return False, third returns True
        mock_query = MagicMock()
        mock_query.filter.return_value.first.side_effect = [None, None, MagicMock()]
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.validate_serial_numbers_unique(serial_numbers)
        
        # Verify result
        assert result is False
        # Verify checks stopped after finding duplicate
        assert mock_session.query.call_count == 3
    
    @pytest.mark.asyncio
    async def test_get_transaction_item_summary(self, repository):
        """Test getting transaction item summary."""
        repo, mock_session = repository
        
        transaction_id = str(uuid4())
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        
        # Mock aggregation result
        mock_result = MagicMock()
        mock_result.total_items = 5
        mock_result.total_quantity = 12
        mock_result.total_amount = 1500.00
        mock_result.total_discount = 150.00
        mock_result.total_tax = 120.00
        mock_result.avg_unit_price = 125.00
        mock_query.with_entities.return_value.first.return_value = mock_result
        
        # Mock warranty count
        mock_query.filter.return_value.count.side_effect = [3, 4]  # warranty count, serial count
        
        # Execute repository method
        result = await repo.get_transaction_item_summary(transaction_id)
        
        # Verify result structure
        assert result["total_items"] == 5
        assert result["total_quantity"] == 12
        assert result["total_amount"] == 1500.00
        assert result["total_discount"] == 150.00
        assert result["total_tax"] == 120.00
        assert result["average_unit_price"] == 125.00
        assert result["items_with_warranty"] == 3
        assert result["items_with_serial_numbers"] == 4
    
    @pytest.mark.asyncio
    async def test_update_pricing(self, repository):
        """Test updating item pricing."""
        repo, mock_session = repository
        
        item_id = uuid4()
        
        # Mock existing model with proper attributes
        mock_model = create_mock_transaction_item_model(
            id=item_id,
            quantity=2,
            unit_price=100.00,
            discount=10.00,
            tax_amount=15.00
        )
        
        # Mock query result
        mock_query = MagicMock()
        mock_query.filter.return_value.first.return_value = mock_model
        mock_session.query.return_value = mock_query
        
        # Execute repository method
        result = await repo.update_pricing(
            item_id=item_id,
            unit_price=Decimal("120.00"),
            discount=Decimal("20.00"),
            tax_amount=Decimal("25.00")
        )
        
        # Verify database operations
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_model)
        
        # Verify pricing was updated
        assert mock_model.unit_price == 120.00
        assert mock_model.discount == 20.00
        assert mock_model.tax_amount == 25.00
        # Verify total price was recalculated: (2 * 120.00) - 20.00 + 25.00 = 245.00
        assert mock_model.total_price == 245.00
        
        # Verify result
        assert isinstance(result, PurchaseTransactionItem)
    
    @pytest.mark.asyncio
    async def test_get_items_with_warranty(self, repository):
        """Test getting items with warranty."""
        repo, mock_session = repository
        
        # Mock query chain
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        
        # Mock results with proper attributes
        mock_models = [
            create_mock_transaction_item_model(warranty_period_type="MONTHS", warranty_period=12),
            create_mock_transaction_item_model(warranty_period_type="YEARS", warranty_period=2)
        ]
        mock_query.all.return_value = mock_models
        
        # Execute repository method
        result = await repo.get_items_with_warranty()
        
        # Verify query building
        mock_session.query.assert_called_once_with(PurchaseTransactionItemModel)
        mock_query.filter.assert_called()  # Should filter for warranty fields not null
        mock_query.order_by.assert_called()
        
        # Verify result
        assert len(result) == 2
        assert all(isinstance(item, PurchaseTransactionItem) for item in result)
    
    def test_entity_to_model_conversion(self, repository):
        """Test converting item entity to database model."""
        repo, mock_session = repository
        
        # Setup test entity
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        warehouse_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=2,
            unit_price=Decimal("150.00"),
            warehouse_id=warehouse_id,
            serial_number=["SN001", "SN002"],
            discount=Decimal("25.00"),
            tax_amount=Decimal("20.00"),
            remarks="Test item",
            warranty_period_type="MONTHS",
            warranty_period=6
        )
        
        # Convert entity to model
        model = repo._entity_to_model(item)
        
        # Verify conversion
        assert model.id == item.id
        assert model.transaction_id == transaction_id
        assert model.inventory_item_id == inventory_item_id
        assert model.warehouse_id == warehouse_id
        assert model.quantity == 2
        assert model.unit_price == 150.00
        assert model.serial_number == ["SN001", "SN002"]
        assert model.discount == 25.00
        assert model.tax_amount == 20.00
        assert model.total_price == 295.00  # (2 * 150.00) - 25.00 + 20.00 = 295.00
        assert model.remarks == "Test item"
        assert model.warranty_period_type == "MONTHS"
        assert model.warranty_period == 6
        assert model.created_at == item.created_at
        assert model.updated_at == item.updated_at
        assert model.created_by == item.created_by
        assert model.is_active == item.is_active
    
    def test_model_to_entity_conversion(self, repository):
        """Test converting database model to item entity."""
        repo, mock_session = repository
        
        # Setup test model
        model_id = uuid4()
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        warehouse_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        model = MagicMock()
        model.id = model_id
        model.transaction_id = transaction_id
        model.inventory_item_id = inventory_item_id
        model.warehouse_id = warehouse_id
        model.quantity = 3
        model.unit_price = 200.00
        model.discount = 40.00
        model.tax_amount = 30.00
        model.total_price = 590.00
        model.serial_number = ["SN001", "SN002", "SN003"]
        model.remarks = "Test conversion"
        model.warranty_period_type = "YEARS"
        model.warranty_period = 2
        model.created_at = created_at
        model.updated_at = created_at
        model.created_by = "test_user"
        model.is_active = True
        
        # Convert model to entity
        entity = repo._model_to_entity(model)
        
        # Verify conversion
        assert entity.id == model_id
        assert entity.transaction_id == transaction_id
        assert entity.inventory_item_id == inventory_item_id
        assert entity.warehouse_id == warehouse_id
        assert entity.quantity == 3
        assert entity.unit_price == Decimal("200.00")
        assert entity.discount == Decimal("40.00")
        assert entity.tax_amount == Decimal("30.00")
        assert entity.total_price == Decimal("590.00")
        assert entity.serial_number == ["SN001", "SN002", "SN003"]
        assert entity.remarks == "Test conversion"
        assert entity.warranty_period_type == "YEARS"
        assert entity.warranty_period == 2
        assert entity.created_at == created_at
        assert entity.updated_at == created_at
        assert entity.created_by == "test_user"
        assert entity.is_active is True
    
    def test_model_to_entity_conversion_empty_serial_numbers(self, repository):
        """Test converting model with None serial numbers."""
        repo, mock_session = repository
        
        # Setup test model with None serial numbers
        model = MagicMock()
        model.id = uuid4()
        model.transaction_id = uuid4()
        model.inventory_item_id = uuid4()
        model.warehouse_id = None
        model.quantity = 1
        model.unit_price = 100.00
        model.discount = 0.00
        model.tax_amount = 0.00
        model.total_price = 100.00
        model.serial_number = None  # Test None case
        model.remarks = None
        model.warranty_period_type = None
        model.warranty_period = None
        model.created_at = datetime.now(timezone.utc)
        model.updated_at = datetime.now(timezone.utc)
        model.created_by = None
        model.is_active = True
        
        # Convert model to entity
        entity = repo._model_to_entity(model)
        
        # Verify serial_number defaults to empty list
        assert entity.serial_number == []
    
    def test_model_to_entity_conversion_none(self, repository):
        """Test converting None model returns None."""
        repo, mock_session = repository
        
        # Convert None model
        entity = repo._model_to_entity(None)
        
        # Verify result
        assert entity is None