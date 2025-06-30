"""Tests for CreateSalesTransactionUseCase"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.sales import CreateSalesTransactionUseCase
from src.domain.entities.sales import SalesTransaction, SalesTransactionItem
from src.domain.entities.customer import Customer
from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.domain.value_objects.sales import PaymentTerms


class TestCreateSalesTransactionUseCase:
    """Test suite for CreateSalesTransactionUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_sales_transaction_repository, mock_sales_transaction_item_repository,
                 mock_customer_repository, mock_inventory_repository, mock_id_manager_repository,
                 mock_inventory_stock_movement_service):
        """Create use case instance with mocked dependencies"""
        # Need warehouse repository too
        mock_warehouse_repository = Mock()
        mock_warehouse_repository.find_by_id = AsyncMock()
        
        return CreateSalesTransactionUseCase(
            sales_repository=mock_sales_transaction_repository,
            sales_item_repository=mock_sales_transaction_item_repository,
            customer_repository=mock_customer_repository,
            inventory_repository=mock_inventory_repository,
            warehouse_repository=mock_warehouse_repository,
            id_manager_repository=mock_id_manager_repository,
            stock_movement_service=mock_inventory_stock_movement_service
        )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_success(self, use_case, sample_customer, 
                                                   sample_inventory_item, sample_warehouse):
        """Test successful sales transaction creation"""
        # Setup mock returns
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.return_value = sample_inventory_item
        use_case.warehouse_repository.find_by_id.return_value = sample_warehouse
        use_case.id_manager_repository.get_next_id.return_value = "SO-2024-001"
        use_case.stock_movement_service.check_availability.return_value = True
        
        # Mock repository save methods
        saved_transaction = None
        async def save_transaction(transaction):
            nonlocal saved_transaction
            saved_transaction = transaction
            # ID is already set in entity constructor, just return it
            return transaction
        
        use_case.sales_repository.create.side_effect = save_transaction
        use_case.sales_item_repository.create_many.return_value = []
        
        # Test data
        items = [
            {
                "inventory_item_master_id": sample_inventory_item.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 2,
                "unit_price": Decimal("100.00"),
                "discount_percentage": Decimal("10.0"),
                "tax_rate": Decimal("8.0"),
                "serial_numbers": ["SN001", "SN002"]
            }
        ]
        
        # Execute
        transaction, transaction_items = await use_case.execute(
            customer_id=sample_customer.id,
            items=items,
            shipping_amount=Decimal("25.00"),
            payment_terms="NET_30",
            shipping_address="123 Test St",
            billing_address="456 Bill Ave",
            notes="Test order"
        )
        
        # Assert
        assert isinstance(transaction, SalesTransaction)
        assert transaction.customer_id == sample_customer.id
        assert transaction.transaction_id == "SO-2024-001"
        assert transaction.payment_terms == PaymentTerms.NET_30
        assert transaction.shipping_amount == Decimal("25.00")
        
        # Verify stock was reserved
        use_case.stock_movement_service.reserve_stock.assert_called_once()
        
        # Verify repositories were called
        use_case.customer_repository.find_by_id.assert_called_once_with(sample_customer.id)
        use_case.id_manager_repository.get_next_id.assert_called_once_with(CreateSalesTransactionUseCase.SALES_TRANSACTION_PREFIX)
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_customer_not_found(self, use_case):
        """Test transaction creation with non-existent customer"""
        use_case.customer_repository.find_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Customer .* not found"):
            await use_case.execute(
                customer_id=uuid4(),
                items=[],
                payment_terms="NET_30"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_inactive_customer(self, use_case, sample_customer):
        """Test transaction creation with inactive customer"""
        sample_customer.is_active = False
        use_case.customer_repository.find_by_id.return_value = sample_customer
        
        with pytest.raises(ValueError, match="Customer .* is not active"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=[],
                payment_terms="NET_30"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_invalid_payment_terms(self, use_case, sample_customer):
        """Test transaction creation with invalid payment terms"""
        use_case.customer_repository.find_by_id.return_value = sample_customer
        
        with pytest.raises(ValueError, match="Invalid payment terms"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=[],
                payment_terms="INVALID_TERMS"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_empty_items(self, use_case, sample_customer):
        """Test transaction creation with no items"""
        use_case.customer_repository.find_by_id.return_value = sample_customer
        
        with pytest.raises(ValueError, match="At least one item is required"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=[],
                payment_terms="NET_30"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_inventory_not_found(self, use_case, sample_customer):
        """Test transaction creation with non-existent inventory item"""
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.return_value = None
        
        items = [{
            "inventory_item_master_id": uuid4(),
            "warehouse_id": uuid4(),
            "quantity": 1,
            "unit_price": 100.00
        }]
        
        with pytest.raises(ValueError, match="Inventory item .* not found"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=items,
                payment_terms="NET_30"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_insufficient_stock(self, use_case, sample_customer,
                                                             sample_inventory_item):
        """Test transaction creation with insufficient stock"""
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.return_value = sample_inventory_item
        use_case.stock_movement_service.check_availability.return_value = False
        
        items = [{
            "inventory_item_master_id": sample_inventory_item.id,
            "warehouse_id": uuid4(),
            "quantity": 100,  # More than available
            "unit_price": 100.00
        }]
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=items,
                payment_terms="NET_30"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_with_bulk_discount(self, use_case, sample_customer,
                                                             sample_inventory_item, sample_warehouse):
        """Test transaction creation with bulk discount applied"""
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.return_value = sample_inventory_item
        use_case.id_manager_repository.get_next_id.return_value = "SO-2024-002"
        use_case.stock_movement_service.check_availability.return_value = True
        
        # Mock save
        async def save_transaction(transaction):
            transaction.id = uuid4()
            return transaction
        
        use_case.sales_transaction_repository.create.side_effect = save_transaction
        use_case.sales_transaction_item_repository.create_many.return_value = []
        
        # Large quantity to trigger bulk discount
        items = [{
            "inventory_item_master_id": sample_inventory_item.id,
            "warehouse_id": sample_warehouse.id,
            "quantity": 15,  # Should trigger 5% discount
            "unit_price": 100.00,
            "discount_percentage": 0.0,
            "tax_rate": 10.0
        }]
        
        transaction, transaction_items = await use_case.execute(
            customer_id=sample_customer.id,
            items=items,
            payment_terms="NET_30"
        )
        
        # Verify bulk discount was applied
        assert transaction.discount_amount > Decimal("0.00")
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_with_multiple_items(self, use_case, sample_customer,
                                                               sample_warehouse):
        """Test transaction creation with multiple items"""
        # Create multiple inventory items
        item1 = Mock(id=uuid4(), is_active=True)
        item2 = Mock(id=uuid4(), is_active=True)
        
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.side_effect = [item1, item2]
        use_case.id_manager_repository.get_next_id.return_value = "SO-2024-003"
        use_case.stock_movement_service.check_availability.return_value = True
        
        # Mock save
        async def save_transaction(transaction):
            transaction.id = uuid4()
            return transaction
        
        use_case.sales_transaction_repository.create.side_effect = save_transaction
        use_case.sales_transaction_item_repository.create_many.return_value = []
        
        items = [
            {
                "inventory_item_master_id": item1.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 2,
                "unit_price": 100.00,
                "tax_rate": 10.0
            },
            {
                "inventory_item_master_id": item2.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 3,
                "unit_price": 50.00,
                "tax_rate": 8.0
            }
        ]
        
        transaction, transaction_items = await use_case.execute(
            customer_id=sample_customer.id,
            items=items,
            payment_terms="IMMEDIATE"
        )
        
        # Verify totals
        # Item 1: 2 * 100 = 200, tax = 20, total = 220
        # Item 2: 3 * 50 = 150, tax = 12, total = 162
        # Grand total = 382
        expected_subtotal = Decimal("350.00")
        expected_tax = Decimal("32.00")
        
        assert transaction.subtotal == expected_subtotal
        assert transaction.tax_amount == expected_tax
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_credit_limit_check(self, use_case, sample_customer,
                                                             sample_inventory_item, sample_warehouse):
        """Test credit limit validation"""
        # Set customer credit limit
        sample_customer.credit_limit = Decimal("500.00")
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.return_value = sample_inventory_item
        use_case.stock_movement_service.check_availability.return_value = True
        
        # Mock existing outstanding balance
        use_case.sales_transaction_repository.get_outstanding_balance = AsyncMock(
            return_value=Decimal("400.00")
        )
        
        # Try to create order that would exceed credit limit
        items = [{
            "inventory_item_master_id": sample_inventory_item.id,
            "warehouse_id": sample_warehouse.id,
            "quantity": 2,
            "unit_price": 100.00,  # Total = 200, outstanding = 400, limit = 500
            "tax_rate": 0.0
        }]
        
        with pytest.raises(ValueError, match="exceeds credit limit"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=items,
                payment_terms="NET_30"
            )
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_serial_number_validation(self, use_case, sample_customer,
                                                                   sample_inventory_item, sample_warehouse):
        """Test serial number validation for individual tracking items"""
        sample_inventory_item.tracking_type = "INDIVIDUAL"
        use_case.customer_repository.find_by_id.return_value = sample_customer
        use_case.inventory_repository.find_by_id.return_value = sample_inventory_item
        use_case.stock_movement_service.check_availability.return_value = True
        
        # Quantity doesn't match serial numbers
        items = [{
            "inventory_item_master_id": sample_inventory_item.id,
            "warehouse_id": sample_warehouse.id,
            "quantity": 3,
            "unit_price": 100.00,
            "serial_numbers": ["SN001", "SN002"]  # Only 2 serials for quantity 3
        }]
        
        with pytest.raises(ValueError, match="Serial numbers count.*does not match quantity"):
            await use_case.execute(
                customer_id=sample_customer.id,
                items=items,
                payment_terms="COD"
            )