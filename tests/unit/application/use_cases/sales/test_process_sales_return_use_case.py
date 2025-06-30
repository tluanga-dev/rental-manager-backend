"""Tests for ProcessSalesReturnUseCase"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.application.use_cases.sales import ProcessSalesReturnUseCase
from src.domain.entities.sales import SalesTransaction, SalesTransactionItem, SalesReturn
from src.domain.value_objects.sales import SalesStatus, PaymentStatus


class TestProcessSalesReturnUseCase:
    """Test suite for ProcessSalesReturnUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_sales_transaction_repository, mock_sales_transaction_item_repository,
                 mock_sales_return_repository, mock_sales_return_item_repository,
                 mock_id_manager_repository, mock_inventory_stock_movement_service):
        """Create use case instance with mocked dependencies"""
        return ProcessSalesReturnUseCase(
            sales_repository=mock_sales_transaction_repository,
            sales_item_repository=mock_sales_transaction_item_repository,
            return_repository=mock_sales_return_repository,
            return_item_repository=mock_sales_return_item_repository,
            id_manager_repository=mock_id_manager_repository,
            stock_movement_service=mock_inventory_stock_movement_service
        )
    
    @pytest.mark.asyncio
    async def test_process_return_success(self, use_case, sample_sales_transaction,
                                        sample_sales_transaction_item):
        """Test successful sales return processing"""
        # Setup
        sample_sales_transaction.status = SalesStatus.DELIVERED
        sample_sales_transaction.grand_total = Decimal("1000.00")
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = sample_sales_transaction_item
        use_case.sales_item_repository.get_by_transaction.return_value = [sample_sales_transaction_item]
        use_case.id_manager_repository.get_next_id.return_value = "RET-2024-001"
        
        # Mock save
        async def save_return(sales_return):
            sales_return.id = uuid4()
            return sales_return
        
        use_case.return_repository.create.side_effect = save_return
        use_case.return_item_repository.create_many.return_value = []
        
        # Test data
        items = [{
            "sales_item_id": sample_sales_transaction_item.id,
            "quantity": 1,
            "condition": "GOOD",
            "serial_numbers": ["SN001"]
        }]
        
        # Execute
        result = await use_case.execute(
            sales_transaction_id=sample_sales_transaction.id,
            reason="Product not as expected",
            items=items,
            restocking_fee=10.0  # 10% fee
        )
        
        # Assert
        assert isinstance(result, SalesReturn)
        assert result.return_id == "RET-2024-001"
        assert result.reason == "Product not as expected"
        assert result.refund_amount == sample_sales_transaction_item.total
        assert result.restocking_fee == sample_sales_transaction_item.total * Decimal("0.10")
        
        # Verify stock was processed
        use_case.stock_movement_service.process_return.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_return_transaction_not_found(self, use_case):
        """Test return for non-existent transaction"""
        use_case.sales_repository.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Sales transaction .* not found"):
            await use_case.execute(
                sales_transaction_id=uuid4(),
                reason="Test",
                items=[]
            )
    
    @pytest.mark.asyncio
    async def test_process_return_invalid_status(self, use_case, sample_sales_transaction):
        """Test return for transaction with invalid status"""
        sample_sales_transaction.status = SalesStatus.DRAFT
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Can only return delivered or shipped transactions"):
            await use_case.execute(
                sales_transaction_id=sample_sales_transaction.id,
                reason="Test",
                items=[]
            )
    
    @pytest.mark.asyncio
    async def test_process_return_item_not_found(self, use_case, sample_sales_transaction):
        """Test return with non-existent item"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = None
        
        items = [{
            "sales_item_id": uuid4(),
            "quantity": 1,
            "condition": "GOOD"
        }]
        
        with pytest.raises(ValueError, match="Sales item .* not found"):
            await use_case.execute(
                sales_transaction_id=sample_sales_transaction.id,
                reason="Test",
                items=items
            )
    
    @pytest.mark.asyncio
    async def test_process_return_item_wrong_transaction(self, use_case, sample_sales_transaction,
                                                       sample_sales_transaction_item):
        """Test return with item from different transaction"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        sample_sales_transaction_item.transaction_id = uuid4()  # Different transaction
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = sample_sales_transaction_item
        
        items = [{
            "sales_item_id": sample_sales_transaction_item.id,
            "quantity": 1,
            "condition": "GOOD"
        }]
        
        with pytest.raises(ValueError, match="does not belong to this transaction"):
            await use_case.execute(
                sales_transaction_id=sample_sales_transaction.id,
                reason="Test",
                items=items
            )
    
    @pytest.mark.asyncio
    async def test_process_return_excessive_quantity(self, use_case, sample_sales_transaction,
                                                   sample_sales_transaction_item):
        """Test return with quantity exceeding original"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        sample_sales_transaction_item.quantity = 5
        sample_sales_transaction_item.transaction_id = sample_sales_transaction.id
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = sample_sales_transaction_item
        use_case.return_repository.get_by_transaction.return_value = []  # No existing returns
        
        items = [{
            "sales_item_id": sample_sales_transaction_item.id,
            "quantity": 10,  # More than original 5
            "condition": "GOOD"
        }]
        
        with pytest.raises(ValueError, match="Return quantity .* exceeds available quantity"):
            await use_case.execute(
                sales_transaction_id=sample_sales_transaction.id,
                reason="Test",
                items=items
            )
    
    @pytest.mark.asyncio
    async def test_process_return_with_existing_returns(self, use_case, sample_sales_transaction,
                                                      sample_sales_transaction_item):
        """Test return considering existing returns"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        sample_sales_transaction_item.quantity = 5
        sample_sales_transaction_item.transaction_id = sample_sales_transaction.id
        
        # Mock existing return of 2 items
        existing_return_item = Mock(sales_item_id=sample_sales_transaction_item.id, quantity=2)
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = sample_sales_transaction_item
        use_case.sales_item_repository.get_by_transaction.return_value = [sample_sales_transaction_item]
        use_case.return_repository.get_by_transaction.return_value = [Mock(id=uuid4())]
        use_case.return_item_repository.get_by_sales_item.return_value = [existing_return_item]
        use_case.id_manager_repository.get_next_id.return_value = "RET-2024-002"
        
        # Mock save
        async def save_return(sales_return):
            sales_return.id = uuid4()
            return sales_return
        
        use_case.return_repository.create.side_effect = save_return
        
        # Try to return 4 more (would exceed original 5)
        items = [{
            "sales_item_id": sample_sales_transaction_item.id,
            "quantity": 4,
            "condition": "DAMAGED"
        }]
        
        with pytest.raises(ValueError, match="Return quantity .* exceeds available quantity"):
            await use_case.execute(
                sales_transaction_id=sample_sales_transaction.id,
                reason="Damaged items",
                items=items
            )
    
    @pytest.mark.asyncio
    async def test_process_return_multiple_items(self, use_case, sample_sales_transaction):
        """Test return with multiple items"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        
        # Create multiple items
        item1 = Mock(
            id=uuid4(),
            transaction_id=sample_sales_transaction.id,
            quantity=3,
            total=Decimal("300.00")
        )
        item2 = Mock(
            id=uuid4(),
            transaction_id=sample_sales_transaction.id,
            quantity=2,
            total=Decimal("200.00")
        )
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.side_effect = [item1, item2]
        use_case.sales_item_repository.get_by_transaction.return_value = [item1, item2]
        use_case.return_repository.get_by_transaction.return_value = []
        use_case.id_manager_repository.get_next_id.return_value = "RET-2024-003"
        
        # Mock save
        async def save_return(sales_return):
            sales_return.id = uuid4()
            return sales_return
        
        use_case.return_repository.create.side_effect = save_return
        use_case.return_item_repository.create_many.return_value = []
        
        items = [
            {
                "sales_item_id": item1.id,
                "quantity": 2,
                "condition": "GOOD",
                "serial_numbers": ["SN001", "SN002"]
            },
            {
                "sales_item_id": item2.id,
                "quantity": 1,
                "condition": "DAMAGED",
                "serial_numbers": ["SN003"]
            }
        ]
        
        result = await use_case.execute(
            sales_transaction_id=sample_sales_transaction.id,
            reason="Mixed return",
            items=items,
            restocking_fee=5.0  # 5% fee
        )
        
        # Total refund: (2/3 * 300) + (1/2 * 200) = 200 + 100 = 300
        expected_refund = Decimal("300.00")
        expected_fee = expected_refund * Decimal("0.05")
        
        assert result.refund_amount == expected_refund
        assert result.restocking_fee == expected_fee
    
    @pytest.mark.asyncio
    async def test_process_return_no_restocking_fee(self, use_case, sample_sales_transaction,
                                                   sample_sales_transaction_item):
        """Test return with no restocking fee"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        sample_sales_transaction_item.transaction_id = sample_sales_transaction.id
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = sample_sales_transaction_item
        use_case.sales_item_repository.get_by_transaction.return_value = [sample_sales_transaction_item]
        use_case.id_manager_repository.get_next_id.return_value = "RET-2024-004"
        
        # Mock save
        async def save_return(sales_return):
            sales_return.id = uuid4()
            return sales_return
        
        use_case.return_repository.create.side_effect = save_return
        
        items = [{
            "sales_item_id": sample_sales_transaction_item.id,
            "quantity": 1,
            "condition": "DEFECTIVE"
        }]
        
        result = await use_case.execute(
            sales_transaction_id=sample_sales_transaction.id,
            reason="Defective product",
            items=items,
            restocking_fee=0.0  # No fee for defective items
        )
        
        assert result.restocking_fee == Decimal("0.00")
        assert result.net_refund_amount == result.refund_amount
    
    @pytest.mark.asyncio
    async def test_process_return_serial_number_validation(self, use_case, sample_sales_transaction,
                                                         sample_sales_transaction_item):
        """Test return with serial number validation"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        sample_sales_transaction_item.transaction_id = sample_sales_transaction.id
        sample_sales_transaction_item.serial_numbers = ["SN001", "SN002", "SN003"]
        
        use_case.sales_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_item_repository.get_by_id.return_value = sample_sales_transaction_item
        
        # Try to return serial number not in original sale
        items = [{
            "sales_item_id": sample_sales_transaction_item.id,
            "quantity": 1,
            "condition": "GOOD",
            "serial_numbers": ["SN999"]  # Not in original
        }]
        
        with pytest.raises(ValueError, match="Serial number .* not found in original sale"):
            await use_case.execute(
                sales_transaction_id=sample_sales_transaction.id,
                reason="Test",
                items=items
            )