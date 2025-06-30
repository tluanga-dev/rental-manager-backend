"""
Comprehensive integration tests for Purchase Order API endpoints.

This module tests all purchase order API endpoints with proper mocking
and covers various scenarios including success, validation errors, and edge cases.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.api.v1.endpoints.purchase_orders import router as purchase_order_router
from src.domain.entities.purchase_order import PurchaseOrder, PurchaseOrderStatus
from src.domain.entities.purchase_order_line_item import PurchaseOrderLineItem


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(purchase_order_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_purchase_order_service():
    """Mock purchase order service"""
    service = Mock()
    service.create_purchase_order = AsyncMock()
    service.get_purchase_order = AsyncMock()
    service.get_purchase_order_details = AsyncMock()
    service.update_purchase_order = AsyncMock()
    service.delete_purchase_order = AsyncMock()
    service.list_purchase_orders = AsyncMock()
    service.search_purchase_orders = AsyncMock()
    service.mark_as_ordered = AsyncMock()
    service.cancel_purchase_order = AsyncMock()
    service.receive_items = AsyncMock()
    service.get_purchase_order_summary = AsyncMock()
    
    # Mock repository for vendor lookup
    service.vendor_repository = Mock()
    service.vendor_repository.find_by_id = AsyncMock()
    
    return service


@pytest.mark.integration
class TestPurchaseOrderAPI:
    """Integration tests for Purchase Order API endpoints"""

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_create_purchase_order_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order,
        sample_vendor,
        sample_inventory_item,
        sample_warehouse
    ):
        """Test successful purchase order creation"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.create_purchase_order.return_value = sample_purchase_order

        request_data = {
            "vendor_id": str(sample_vendor.id),
            "order_date": str(date.today()),
            "expected_delivery_date": str(date.today() + timedelta(days=7)),
            "reference_number": "REF-001",
            "invoice_number": "INV-001",
            "notes": "Test purchase order",
            "created_by": "test_user",
            "items": [
                {
                    "inventory_item_master_id": str(sample_inventory_item.id),
                    "warehouse_id": str(sample_warehouse.id),
                    "quantity": 2,
                    "unit_price": 100.00,
                    "discount": 10.00,
                    "tax_amount": 18.00,
                    "serial_number": "TEST-SN-001",
                    "rental_rate": 25.00,
                    "replacement_cost": 500.00,
                    "rentable": True,
                    "sellable": False
                }
            ]
        }

        response = client.post("/purchase-orders/", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["order_number"] == sample_purchase_order.order_number
        assert data["vendor_id"] == str(sample_purchase_order.vendor_id)
        assert data["status"] == sample_purchase_order.status.value

        mock_purchase_order_service.create_purchase_order.assert_called_once()

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_create_purchase_order_with_multiple_items(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order,
        sample_vendor,
        sample_inventory_item,
        sample_warehouse
    ):
        """Test purchase order creation with multiple items"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.create_purchase_order.return_value = sample_purchase_order

        request_data = {
            "vendor_id": str(sample_vendor.id),
            "order_date": str(date.today()),
            "created_by": "test_user",
            "items": [
                {
                    "inventory_item_master_id": str(sample_inventory_item.id),
                    "warehouse_id": str(sample_warehouse.id),
                    "quantity": 2,
                    "unit_price": 100.00,
                    "serial_number": "TEST-SN-001"
                },
                {
                    "inventory_item_master_id": str(sample_inventory_item.id),
                    "warehouse_id": str(sample_warehouse.id),
                    "quantity": 1,
                    "unit_price": 200.00,
                    "serial_number": "TEST-SN-002"
                }
            ]
        }

        response = client.post("/purchase-orders/", json=request_data)

        assert response.status_code == 201
        data = response.json()
        assert data["order_number"] == sample_purchase_order.order_number

        # Verify the service was called with the correct number of items
        call_args = mock_purchase_order_service.create_purchase_order.call_args
        assert len(call_args.kwargs["items"]) == 2

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_create_purchase_order_validation_error(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order creation with validation error"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.create_purchase_order.side_effect = ValueError("Vendor not found")

        request_data = {
            "vendor_id": str(uuid4()),
            "order_date": str(date.today()),
            "created_by": "test_user",
            "items": []
        }

        response = client.post("/purchase-orders/", json=request_data)

        assert response.status_code == 400
        assert "Vendor not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_get_purchase_order_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order,
        sample_purchase_order_line_item,
        sample_vendor
    ):
        """Test successful purchase order retrieval with details"""
        mock_get_service.return_value = mock_purchase_order_service
        
        # Mock the details response
        details = {
            "purchase_order": sample_purchase_order,
            "line_items": [sample_purchase_order_line_item],
            "total_items": 1,
            "items_received": 0,
            "items_pending": 1
        }
        mock_purchase_order_service.get_purchase_order_details.return_value = details
        mock_purchase_order_service.vendor_repository.find_by_id.return_value = sample_vendor

        purchase_order_id = uuid4()
        response = client.get(f"/purchase-orders/{purchase_order_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["order_number"] == sample_purchase_order.order_number
        assert data["vendor_name"] == sample_vendor.name
        assert len(data["line_items"]) == 1
        assert data["total_items"] == 1

        mock_purchase_order_service.get_purchase_order_details.assert_called_once_with(purchase_order_id)

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_get_purchase_order_not_found(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order retrieval when not found"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.get_purchase_order_details.side_effect = ValueError("Purchase order not found")

        purchase_order_id = uuid4()
        response = client.get(f"/purchase-orders/{purchase_order_id}")

        assert response.status_code == 404
        assert "Purchase order not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_update_purchase_order_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test successful purchase order update"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.update_purchase_order.return_value = sample_purchase_order

        purchase_order_id = uuid4()
        update_data = {
            "notes": "Updated notes",
            "reference_number": "UPDATED-REF-001"
        }

        response = client.put(f"/purchase-orders/{purchase_order_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["order_number"] == sample_purchase_order.order_number

        mock_purchase_order_service.update_purchase_order.assert_called_once()

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_update_purchase_order_not_found(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order update when not found"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.update_purchase_order.side_effect = ValueError("Purchase order not found")

        purchase_order_id = uuid4()
        update_data = {"notes": "Updated notes"}

        response = client.put(f"/purchase-orders/{purchase_order_id}", json=update_data)

        assert response.status_code == 400
        assert "Purchase order not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_receive_purchase_order_items_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test successful purchase order item receipt"""
        mock_get_service.return_value = mock_purchase_order_service
        sample_purchase_order._status = PurchaseOrderStatus.PARTIAL_RECEIVED
        mock_purchase_order_service.receive_items.return_value = sample_purchase_order

        purchase_order_id = uuid4()
        receive_data = {
            "received_items": [
                {
                    "line_item_id": str(uuid4()),
                    "quantity": 2
                }
            ]
        }

        response = client.post(f"/purchase-orders/{purchase_order_id}/receive", json=receive_data)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == PurchaseOrderStatus.PARTIAL_RECEIVED.value

        mock_purchase_order_service.receive_items.assert_called_once()

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_receive_purchase_order_items_validation_error(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order item receipt with validation error"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.receive_items.side_effect = ValueError("Line item not found")

        purchase_order_id = uuid4()
        receive_data = {
            "received_items": [
                {
                    "line_item_id": str(uuid4()),
                    "quantity": 5
                }
            ]
        }

        response = client.post(f"/purchase-orders/{purchase_order_id}/receive", json=receive_data)

        assert response.status_code == 400
        assert "Line item not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_mark_purchase_order_as_ordered_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test marking purchase order as ordered"""
        mock_get_service.return_value = mock_purchase_order_service
        sample_purchase_order._status = PurchaseOrderStatus.ORDERED
        mock_purchase_order_service.mark_as_ordered.return_value = sample_purchase_order

        purchase_order_id = uuid4()
        response = client.post(f"/purchase-orders/{purchase_order_id}/mark-as-ordered")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == PurchaseOrderStatus.ORDERED.value

        mock_purchase_order_service.mark_as_ordered.assert_called_once_with(purchase_order_id)

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_cancel_purchase_order_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test successful purchase order cancellation"""
        mock_get_service.return_value = mock_purchase_order_service
        sample_purchase_order._status = PurchaseOrderStatus.CANCELLED
        mock_purchase_order_service.cancel_purchase_order.return_value = sample_purchase_order

        purchase_order_id = uuid4()
        response = client.post(f"/purchase-orders/{purchase_order_id}/cancel")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == PurchaseOrderStatus.CANCELLED.value

        mock_purchase_order_service.cancel_purchase_order.assert_called_once_with(purchase_order_id)

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_cancel_purchase_order_validation_error(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order cancellation with validation error"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.cancel_purchase_order.side_effect = ValueError("Cannot cancel received order")

        purchase_order_id = uuid4()
        response = client.post(f"/purchase-orders/{purchase_order_id}/cancel")

        assert response.status_code == 400
        assert "Cannot cancel received order" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_list_purchase_orders_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test successful purchase orders listing"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.list_purchase_orders.return_value = [sample_purchase_order]

        response = client.get("/purchase-orders/?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_number"] == sample_purchase_order.order_number

        mock_purchase_order_service.list_purchase_orders.assert_called_once()

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_list_purchase_orders_with_filters(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order,
        sample_vendor
    ):
        """Test purchase orders listing with filters"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.list_purchase_orders.return_value = [sample_purchase_order]

        query_params = {
            "vendor_id": str(sample_vendor.id),
            "status": "PENDING",
            "start_date": str(date.today() - timedelta(days=7)),
            "end_date": str(date.today()),
            "skip": 0,
            "limit": 20
        }

        response = client.get("/purchase-orders/", params=query_params)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify service was called with correct parameters
        call_args = mock_purchase_order_service.list_purchase_orders.call_args
        assert call_args.kwargs["vendor_id"] == sample_vendor.id
        assert call_args.kwargs["status"].value == "PENDING"

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_search_purchase_orders_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test successful purchase orders search"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.search_purchase_orders.return_value = [sample_purchase_order]

        search_data = {
            "query": "PO-2024",
            "search_fields": ["order_number", "reference_number"],
            "limit": 10
        }

        response = client.post("/purchase-orders/search", json=search_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["order_number"] == sample_purchase_order.order_number

        mock_purchase_order_service.search_purchase_orders.assert_called_once()

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_search_purchase_orders_with_query_only(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_purchase_order
    ):
        """Test purchase orders search with query only"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.search_purchase_orders.return_value = [sample_purchase_order]

        search_data = {
            "query": "Acme",
            "limit": 5
        }

        response = client.post("/purchase-orders/search", json=search_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify service was called with correct parameters
        call_args = mock_purchase_order_service.search_purchase_orders.call_args
        assert call_args.kwargs["query"] == "Acme"
        assert call_args.kwargs["search_fields"] is None
        assert call_args.kwargs["limit"] == 5

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_get_purchase_order_summary_success(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test successful purchase order summary retrieval"""
        mock_get_service.return_value = mock_purchase_order_service
        
        summary_data = {
            "purchase_order_id": str(uuid4()),
            "order_number": "PO-2024-001",
            "vendor_name": "Acme Corp",
            "status": "PENDING",
            "total_amount": 500.00,
            "total_items": 3,
            "items_received": 1,
            "items_pending": 2,
            "completion_percentage": 33.33
        }
        mock_purchase_order_service.get_purchase_order_summary.return_value = summary_data

        purchase_order_id = uuid4()
        response = client.get(f"/purchase-orders/{purchase_order_id}/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["order_number"] == "PO-2024-001"
        assert data["vendor_name"] == "Acme Corp"
        assert data["total_items"] == 3
        assert data["completion_percentage"] == 33.33

        mock_purchase_order_service.get_purchase_order_summary.assert_called_once_with(purchase_order_id)

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_get_purchase_order_summary_not_found(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order summary retrieval when not found"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.get_purchase_order_summary.side_effect = ValueError("Purchase order not found")

        purchase_order_id = uuid4()
        response = client.get(f"/purchase-orders/{purchase_order_id}/summary")

        assert response.status_code == 404
        assert "Purchase order not found" in response.json()["detail"]

    # Edge case tests
    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_create_purchase_order_empty_items(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service,
        sample_vendor
    ):
        """Test purchase order creation with empty items list"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.create_purchase_order.side_effect = ValueError("Items list cannot be empty")

        request_data = {
            "vendor_id": str(sample_vendor.id),
            "order_date": str(date.today()),
            "created_by": "test_user",
            "items": []
        }

        response = client.post("/purchase-orders/", json=request_data)

        assert response.status_code == 400
        assert "Items list cannot be empty" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_receive_purchase_order_zero_quantity(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase order item receipt with zero quantity"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.receive_items.side_effect = ValueError("Quantity must be greater than zero")

        purchase_order_id = uuid4()
        receive_data = {
            "received_items": [
                {
                    "line_item_id": str(uuid4()),
                    "quantity": 0
                }
            ]
        }

        response = client.post(f"/purchase-orders/{purchase_order_id}/receive", json=receive_data)

        assert response.status_code == 400
        assert "Quantity must be greater than zero" in response.json()["detail"]

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_list_purchase_orders_with_invalid_status(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test purchase orders listing with invalid status should return 422"""
        mock_get_service.return_value = mock_purchase_order_service

        response = client.get("/purchase-orders/?status=INVALID_STATUS")

        # FastAPI will return 422 for invalid enum values during request validation
        assert response.status_code == 422

    @patch('src.api.v1.endpoints.purchase_orders.get_purchase_order_service')
    def test_internal_server_error_handling(
        self, 
        mock_get_service, 
        client, 
        mock_purchase_order_service
    ):
        """Test internal server error handling"""
        mock_get_service.return_value = mock_purchase_order_service
        mock_purchase_order_service.list_purchase_orders.side_effect = Exception("Database connection failed")

        response = client.get("/purchase-orders/")

        assert response.status_code == 500
        assert "Failed to list purchase orders" in response.json()["detail"]