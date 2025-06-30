"""
Comprehensive unit tests for purchase order use cases.

This module tests all purchase order use cases in isolation with proper mocking.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4, UUID
from datetime import date, timedelta
from decimal import Decimal

from src.application.use_cases.purchase_order_use_cases import (
    CreatePurchaseOrderUseCase,
    UpdatePurchaseOrderUseCase,
    ReceivePurchaseOrderUseCase,
    CancelPurchaseOrderUseCase,
    GetPurchaseOrderUseCase,
    GetPurchaseOrderDetailsUseCase,
    ListPurchaseOrdersUseCase,
    SearchPurchaseOrdersUseCase,
)
from src.domain.entities.purchase_order import PurchaseOrder, PurchaseOrderStatus
from src.domain.entities.purchase_order_line_item import PurchaseOrderLineItem


@pytest.mark.asyncio
class TestCreatePurchaseOrderUseCase:
    """Test cases for CreatePurchaseOrderUseCase"""

    async def test_successful_creation_with_single_item(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        mock_vendor_repository,
        mock_inventory_repository,
        sample_vendor,
        sample_inventory_item,
        sample_warehouse,
    ):
        """Test successful purchase order creation with a single item"""
        # Arrange
        vendor_id = sample_vendor.id
        order_date = date.today()
        items = [
            {
                "inventory_item_master_id": sample_inventory_item.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 2,
                "unit_price": 100.00,
                "discount": 10.00,
                "tax_amount": 18.00,
                "serial_number": "TEST-SN-001",
                "rental_rate": 25.00,
                "replacement_cost": 500.00,
                "rentable": True,
                "sellable": False,
            }
        ]

        # Setup mocks
        mock_vendor_repository.find_by_id.return_value = sample_vendor
        mock_inventory_repository.find_by_id.return_value = sample_inventory_item
        mock_purchase_order_repository.get_next_order_number.return_value = "PO-2024-001"
        
        created_po = PurchaseOrder(
            order_number="PO-2024-001",
            vendor_id=vendor_id,
            order_date=order_date,
            created_by="test_user",
        )
        created_po._id = uuid4()
        mock_purchase_order_repository.save.return_value = created_po
        mock_purchase_order_repository.update.return_value = created_po

        created_line_item = PurchaseOrderLineItem(
            purchase_order_id=created_po.id,
            inventory_item_master_id=sample_inventory_item.id,
            warehouse_id=sample_warehouse.id,
            quantity=2,
            unit_price=Decimal("100.00"),
            created_by="test_user",
        )
        created_line_item._id = uuid4()
        mock_purchase_order_line_item_repository.save.return_value = created_line_item

        use_case = CreatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_vendor_repository,
            mock_inventory_repository,
        )

        # Act
        result = await use_case.execute(
            vendor_id=vendor_id,
            order_date=order_date,
            items=items,
            created_by="test_user",
        )

        # Assert
        assert result is not None
        assert result.order_number == "PO-2024-001"
        assert result.vendor_id == vendor_id
        assert result.order_date == order_date

        # Verify repository calls
        mock_vendor_repository.find_by_id.assert_called_once_with(vendor_id)
        mock_inventory_repository.find_by_id.assert_called_once_with(sample_inventory_item.id)
        mock_purchase_order_repository.get_next_order_number.assert_called_once()
        mock_purchase_order_repository.save.assert_called_once()
        mock_purchase_order_line_item_repository.save.assert_called_once()
        mock_purchase_order_repository.update.assert_called_once()

    async def test_creation_with_invalid_vendor(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        mock_vendor_repository,
        mock_inventory_repository,
        sample_inventory_item,
        sample_warehouse,
    ):
        """Test creation fails with invalid vendor"""
        # Arrange
        invalid_vendor_id = uuid4()
        mock_vendor_repository.find_by_id.return_value = None

        use_case = CreatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_vendor_repository,
            mock_inventory_repository,
        )

        items = [
            {
                "inventory_item_master_id": sample_inventory_item.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 1,
                "unit_price": 100.00,
            }
        ]

        # Act & Assert
        with pytest.raises(ValueError, match=f"Vendor with ID {invalid_vendor_id} not found"):
            await use_case.execute(
                vendor_id=invalid_vendor_id,
                order_date=date.today(),
                items=items,
            )

        # Verify only vendor lookup was called
        mock_vendor_repository.find_by_id.assert_called_once_with(invalid_vendor_id)
        mock_purchase_order_repository.get_next_order_number.assert_not_called()

    async def test_creation_with_invalid_inventory_item(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        mock_vendor_repository,
        mock_inventory_repository,
        sample_vendor,
        sample_warehouse,
    ):
        """Test creation fails with invalid inventory item"""
        # Arrange
        invalid_item_id = uuid4()
        mock_vendor_repository.find_by_id.return_value = sample_vendor
        mock_inventory_repository.find_by_id.return_value = None
        mock_purchase_order_repository.get_next_order_number.return_value = "PO-2024-001"

        created_po = PurchaseOrder(
            order_number="PO-2024-001",
            vendor_id=sample_vendor.id,
            order_date=date.today(),
        )
        created_po._id = uuid4()
        mock_purchase_order_repository.save.return_value = created_po

        use_case = CreatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_vendor_repository,
            mock_inventory_repository,
        )

        items = [
            {
                "inventory_item_master_id": invalid_item_id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 1,
                "unit_price": 100.00,
            }
        ]

        # Act & Assert
        with pytest.raises(ValueError, match=f"Inventory item with ID {invalid_item_id} not found"):
            await use_case.execute(
                vendor_id=sample_vendor.id,
                order_date=date.today(),
                items=items,
            )

        # Verify calls
        mock_vendor_repository.find_by_id.assert_called_once()
        mock_purchase_order_repository.save.assert_called_once()
        mock_inventory_repository.find_by_id.assert_called_once_with(invalid_item_id)

    async def test_creation_with_multiple_items(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        mock_vendor_repository,
        mock_inventory_repository,
        sample_vendor,
        sample_inventory_item,
        sample_warehouse,
    ):
        """Test successful creation with multiple items"""
        # Arrange
        items = [
            {
                "inventory_item_master_id": sample_inventory_item.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 2,
                "unit_price": 100.00,
                "discount": 10.00,
                "tax_amount": 18.00,
            },
            {
                "inventory_item_master_id": sample_inventory_item.id,
                "warehouse_id": sample_warehouse.id,
                "quantity": 1,
                "unit_price": 200.00,
                "discount": 0.00,
                "tax_amount": 20.00,
            },
        ]

        # Setup mocks
        mock_vendor_repository.find_by_id.return_value = sample_vendor
        mock_inventory_repository.find_by_id.return_value = sample_inventory_item
        mock_purchase_order_repository.get_next_order_number.return_value = "PO-2024-002"

        created_po = PurchaseOrder(
            order_number="PO-2024-002",
            vendor_id=sample_vendor.id,
            order_date=date.today(),
        )
        created_po._id = uuid4()
        mock_purchase_order_repository.save.return_value = created_po
        mock_purchase_order_repository.update.return_value = created_po

        created_line_item = PurchaseOrderLineItem(
            purchase_order_id=created_po.id,
            inventory_item_master_id=sample_inventory_item.id,
            warehouse_id=sample_warehouse.id,
            quantity=1,
            unit_price=Decimal("100.00"),
        )
        created_line_item._id = uuid4()
        mock_purchase_order_line_item_repository.save.return_value = created_line_item

        use_case = CreatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_vendor_repository,
            mock_inventory_repository,
        )

        # Act
        result = await use_case.execute(
            vendor_id=sample_vendor.id,
            order_date=date.today(),
            items=items,
        )

        # Assert
        assert result is not None
        assert result.order_number == "PO-2024-002"

        # Verify multiple line items were processed
        assert mock_purchase_order_line_item_repository.save.call_count == 2
        assert mock_inventory_repository.find_by_id.call_count == 2


@pytest.mark.asyncio
class TestUpdatePurchaseOrderUseCase:
    """Test cases for UpdatePurchaseOrderUseCase"""

    async def test_successful_update(
        self,
        mock_purchase_order_repository,
        mock_vendor_repository,
        sample_purchase_order,
        sample_vendor,
    ):
        """Test successful purchase order update"""
        # Arrange
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order
        mock_vendor_repository.find_by_id.return_value = sample_vendor
        mock_purchase_order_repository.update.return_value = sample_purchase_order

        use_case = UpdatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_vendor_repository,
        )

        new_notes = "Updated notes"
        new_reference = "NEW-REF-001"

        # Act
        result = await use_case.execute(
            purchase_order_id=sample_purchase_order.id,
            notes=new_notes,
            reference_number=new_reference,
        )

        # Assert
        assert result is not None
        mock_purchase_order_repository.find_by_id.assert_called_once_with(sample_purchase_order.id)
        mock_purchase_order_repository.update.assert_called_once()

    async def test_update_non_existent_order(
        self,
        mock_purchase_order_repository,
        mock_vendor_repository,
    ):
        """Test update fails for non-existent order"""
        # Arrange
        non_existent_id = uuid4()
        mock_purchase_order_repository.find_by_id.return_value = None

        use_case = UpdatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_vendor_repository,
        )

        # Act & Assert
        with pytest.raises(ValueError, match=f"Purchase order with ID {non_existent_id} not found"):
            await use_case.execute(
                purchase_order_id=non_existent_id,
                notes="New notes",
            )

    async def test_update_non_editable_order(
        self,
        mock_purchase_order_repository,
        mock_vendor_repository,
        sample_purchase_order,
    ):
        """Test update fails for non-editable order"""
        # Arrange
        sample_purchase_order._status = PurchaseOrderStatus.RECEIVED  # Non-editable status
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order

        use_case = UpdatePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_vendor_repository,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="cannot be edited"):
            await use_case.execute(
                purchase_order_id=sample_purchase_order.id,
                notes="New notes",
            )


@pytest.mark.asyncio
class TestCancelPurchaseOrderUseCase:
    """Test cases for CancelPurchaseOrderUseCase"""

    async def test_successful_cancellation(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test successful purchase order cancellation"""
        # Arrange
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order
        mock_purchase_order_repository.update.return_value = sample_purchase_order

        use_case = CancelPurchaseOrderUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(sample_purchase_order.id)

        # Assert
        assert result is not None
        assert result.status == PurchaseOrderStatus.CANCELLED
        mock_purchase_order_repository.find_by_id.assert_called_once_with(sample_purchase_order.id)
        mock_purchase_order_repository.update.assert_called_once()

    async def test_cancel_non_existent_order(
        self,
        mock_purchase_order_repository,
    ):
        """Test cancellation fails for non-existent order"""
        # Arrange
        non_existent_id = uuid4()
        mock_purchase_order_repository.find_by_id.return_value = None

        use_case = CancelPurchaseOrderUseCase(mock_purchase_order_repository)

        # Act & Assert
        with pytest.raises(ValueError, match=f"Purchase order with ID {non_existent_id} not found"):
            await use_case.execute(non_existent_id)


@pytest.mark.asyncio
class TestGetPurchaseOrderUseCase:
    """Test cases for GetPurchaseOrderUseCase"""

    async def test_successful_retrieval(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test successful purchase order retrieval"""
        # Arrange
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order

        use_case = GetPurchaseOrderUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(sample_purchase_order.id)

        # Assert
        assert result == sample_purchase_order
        mock_purchase_order_repository.find_by_id.assert_called_once_with(sample_purchase_order.id)

    async def test_retrieval_non_existent_order(
        self,
        mock_purchase_order_repository,
    ):
        """Test retrieval returns None for non-existent order"""
        # Arrange
        non_existent_id = uuid4()
        mock_purchase_order_repository.find_by_id.return_value = None

        use_case = GetPurchaseOrderUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(non_existent_id)

        # Assert
        assert result is None
        mock_purchase_order_repository.find_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.asyncio
class TestGetPurchaseOrderDetailsUseCase:
    """Test cases for GetPurchaseOrderDetailsUseCase"""

    async def test_successful_details_retrieval(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        sample_purchase_order,
        sample_purchase_order_line_item,
    ):
        """Test successful purchase order details retrieval"""
        # Arrange
        line_items = [sample_purchase_order_line_item]
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order
        mock_purchase_order_line_item_repository.find_by_purchase_order.return_value = line_items

        use_case = GetPurchaseOrderDetailsUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
        )

        # Act
        result = await use_case.execute(sample_purchase_order.id)

        # Assert
        assert result["purchase_order"] == sample_purchase_order
        assert result["line_items"] == line_items
        assert result["total_items"] == 1
        assert "items_received" in result
        assert "items_pending" in result

        mock_purchase_order_repository.find_by_id.assert_called_once_with(sample_purchase_order.id)
        mock_purchase_order_line_item_repository.find_by_purchase_order.assert_called_once_with(
            sample_purchase_order.id
        )

    async def test_details_retrieval_non_existent_order(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
    ):
        """Test details retrieval fails for non-existent order"""
        # Arrange
        non_existent_id = uuid4()
        mock_purchase_order_repository.find_by_id.return_value = None

        use_case = GetPurchaseOrderDetailsUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
        )

        # Act & Assert
        with pytest.raises(ValueError, match=f"Purchase order with ID {non_existent_id} not found"):
            await use_case.execute(non_existent_id)


@pytest.mark.asyncio
class TestListPurchaseOrdersUseCase:
    """Test cases for ListPurchaseOrdersUseCase"""

    async def test_list_all_orders(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test listing all purchase orders"""
        # Arrange
        orders = [sample_purchase_order]
        mock_purchase_order_repository.find_all.return_value = orders

        use_case = ListPurchaseOrdersUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(skip=0, limit=100)

        # Assert
        assert result == orders
        mock_purchase_order_repository.find_all.assert_called_once_with(0, 100)

    async def test_list_orders_by_vendor(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
        sample_vendor,
    ):
        """Test listing orders by vendor"""
        # Arrange
        orders = [sample_purchase_order]
        mock_purchase_order_repository.find_by_vendor.return_value = orders

        use_case = ListPurchaseOrdersUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(vendor_id=sample_vendor.id)

        # Assert
        assert result == orders
        mock_purchase_order_repository.find_by_vendor.assert_called_once_with(sample_vendor.id, 0, 100)

    async def test_list_orders_by_status(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test listing orders by status"""
        # Arrange
        orders = [sample_purchase_order]
        mock_purchase_order_repository.find_by_status.return_value = orders

        use_case = ListPurchaseOrdersUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(status=PurchaseOrderStatus.DRAFT)

        # Assert
        assert result == orders
        mock_purchase_order_repository.find_by_status.assert_called_once_with(
            PurchaseOrderStatus.DRAFT, 0, 100
        )

    async def test_list_orders_by_date_range(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test listing orders by date range"""
        # Arrange
        orders = [sample_purchase_order]
        start_date = date.today() - timedelta(days=7)
        end_date = date.today()
        mock_purchase_order_repository.find_by_date_range.return_value = orders

        use_case = ListPurchaseOrdersUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(start_date=start_date, end_date=end_date)

        # Assert
        assert result == orders
        mock_purchase_order_repository.find_by_date_range.assert_called_once_with(
            start_date, end_date, 0, 100
        )


@pytest.mark.asyncio
class TestSearchPurchaseOrdersUseCase:
    """Test cases for SearchPurchaseOrdersUseCase"""

    async def test_search_orders(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test searching purchase orders"""
        # Arrange
        orders = [sample_purchase_order]
        query = "PO-2024"
        mock_purchase_order_repository.search_purchase_orders.return_value = orders

        use_case = SearchPurchaseOrdersUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(query=query)

        # Assert
        assert result == orders
        mock_purchase_order_repository.search_purchase_orders.assert_called_once_with(
            query, None, 10
        )

    async def test_search_orders_with_fields(
        self,
        mock_purchase_order_repository,
        sample_purchase_order,
    ):
        """Test searching orders with specific fields"""
        # Arrange
        orders = [sample_purchase_order]
        query = "Acme"
        search_fields = ["vendor_name", "reference_number"]
        mock_purchase_order_repository.search_purchase_orders.return_value = orders

        use_case = SearchPurchaseOrdersUseCase(mock_purchase_order_repository)

        # Act
        result = await use_case.execute(query=query, search_fields=search_fields, limit=5)

        # Assert
        assert result == orders
        mock_purchase_order_repository.search_purchase_orders.assert_called_once_with(
            query, search_fields, 5
        )


@pytest.mark.asyncio
class TestReceivePurchaseOrderUseCase:
    """Test cases for ReceivePurchaseOrderUseCase"""

    async def test_successful_partial_receipt(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        sample_purchase_order,
        sample_purchase_order_line_item,
    ):
        """Test successful partial receipt of purchase order"""
        # Arrange
        # Make the purchase order approved first
        sample_purchase_order._status = PurchaseOrderStatus.ORDERED
        
        # Setup line item with partial receipt capability
        sample_purchase_order_line_item._quantity_received = 0
        sample_purchase_order_line_item._quantity = 5  # Can receive up to 5
        
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order
        mock_purchase_order_line_item_repository.find_by_id.return_value = sample_purchase_order_line_item
        mock_purchase_order_line_item_repository.update.return_value = sample_purchase_order_line_item
        mock_purchase_order_repository.update.return_value = sample_purchase_order

        # Mock the database session
        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        mock_session.add = Mock()
        mock_session.flush = Mock()
        mock_session.commit = Mock()

        use_case = ReceivePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_session,
        )

        received_items = [
            {
                "line_item_id": sample_purchase_order_line_item.id,
                "quantity": 3,  # Partial receipt
            }
        ]

        # Act
        result = await use_case.execute(sample_purchase_order.id, received_items)

        # Assert
        assert result is not None
        assert result.status == PurchaseOrderStatus.PARTIAL_RECEIVED  # Should be partially received
        
        mock_purchase_order_repository.find_by_id.assert_called_once_with(sample_purchase_order.id)
        mock_purchase_order_line_item_repository.find_by_id.assert_called_once_with(
            sample_purchase_order_line_item.id
        )
        mock_session.commit.assert_called_once()

    async def test_receipt_non_existent_order(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
    ):
        """Test receipt fails for non-existent order"""
        # Arrange
        non_existent_id = uuid4()
        mock_purchase_order_repository.find_by_id.return_value = None
        mock_session = Mock()

        use_case = ReceivePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ValueError, match=f"Purchase order with ID {non_existent_id} not found"):
            await use_case.execute(non_existent_id, [])

    async def test_receipt_non_receivable_order(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        sample_purchase_order,
    ):
        """Test receipt fails for non-receivable order"""
        # Arrange
        sample_purchase_order._status = PurchaseOrderStatus.CANCELLED  # Non-receivable status
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order
        mock_session = Mock()

        use_case = ReceivePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_session,
        )

        # Act & Assert
        with pytest.raises(ValueError, match="cannot receive items"):
            await use_case.execute(sample_purchase_order.id, [])

    async def test_receipt_invalid_line_item(
        self,
        mock_purchase_order_repository,
        mock_purchase_order_line_item_repository,
        sample_purchase_order,
    ):
        """Test receipt fails for invalid line item"""
        # Arrange
        sample_purchase_order._status = PurchaseOrderStatus.ORDERED
        mock_purchase_order_repository.find_by_id.return_value = sample_purchase_order
        mock_purchase_order_line_item_repository.find_by_id.return_value = None
        mock_session = Mock()

        use_case = ReceivePurchaseOrderUseCase(
            mock_purchase_order_repository,
            mock_purchase_order_line_item_repository,
            mock_session,
        )

        invalid_line_item_id = uuid4()
        received_items = [{"line_item_id": invalid_line_item_id, "quantity": 1}]

        # Act & Assert
        with pytest.raises(ValueError, match=f"Line item with ID {invalid_line_item_id} not found"):
            await use_case.execute(sample_purchase_order.id, received_items)