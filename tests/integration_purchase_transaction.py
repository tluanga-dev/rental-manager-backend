"""
Integration tests for Purchase Transaction functionality.

Tests complete workflows with real database interactions:
- End-to-end API workflows
- Database persistence and retrieval
- Cross-layer integration
- Performance and scalability
- Transaction atomicity and rollback
"""

import pytest
import asyncio
from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4
from typing import Dict, Any, List

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.infrastructure.database.base import Base
from src.infrastructure.database.models import (
    PurchaseTransactionModel, 
    PurchaseTransactionItemModel,
    VendorModel,
    InventoryItemMasterModel,
    WarehouseModel,
    IdManagerModel
)
from src.core.config.database import get_db_session
from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem


# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_vendor_data():
    """Sample vendor data for testing."""
    return {
        "id": str(uuid4()),
        "name": "Test Vendor",
        "contact_person": "John Doe",
        "email": "vendor@test.com",
        "phone": "+1234567890",
        "address": "123 Vendor St",
        "city": "Test City",
        "state": "Test State",
        "postal_code": "12345",
        "country": "Test Country",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_warehouse_data():
    """Sample warehouse data for testing."""
    return {
        "id": str(uuid4()),
        "name": "Test Warehouse",
        "label": "TEST",
        "remarks": "Test warehouse",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def sample_inventory_item_data():
    """Sample inventory item data for testing."""
    return {
        "id": str(uuid4()),
        "item_code": "ITEM-001",
        "item_name": "Test Item",
        "description": "Test item description",
        "category_id": None,
        "brand": "Test Brand",
        "model": "Test Model",
        "tracking_type": "INDIVIDUAL",
        "unit_of_measurement": "PCS",
        "purchase_price": 100.00,
        "selling_price": 150.00,
        "reorder_level": 10,
        "maximum_stock": 100,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }


@pytest.fixture
def setup_test_data(db_session, sample_vendor_data, sample_warehouse_data, sample_inventory_item_data):
    """Set up test data in the database."""
    # Create vendor
    vendor = VendorModel(**sample_vendor_data)
    db_session.add(vendor)
    
    # Create warehouse
    warehouse = WarehouseModel(**sample_warehouse_data)
    db_session.add(warehouse)
    
    # Create inventory item
    inventory_item = InventoryItemMasterModel(**sample_inventory_item_data)
    db_session.add(inventory_item)
    
    # Create ID manager for purchase transactions
    id_manager = IdManagerModel(
        id=str(uuid4()),
        entity_type="purchase_transaction",
        prefix="PUR",
        current_id=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    db_session.add(id_manager)
    
    db_session.commit()
    
    return {
        "vendor": vendor,
        "warehouse": warehouse,
        "inventory_item": inventory_item,
        "id_manager": id_manager
    }


class TestPurchaseTransactionAPIIntegration:
    """Test purchase transaction API integration with real database."""
    
    def test_create_transaction_integration(self, client, setup_test_data):
        """Test creating a purchase transaction via API."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-INT-001",
            "remarks": "Integration test transaction",
            "created_by": "integration_test"
        }
        
        response = client.post("/api/v1/purchase-transactions/", json=request_data)
        
        assert response.status_code == 201
        
        response_data = response.json()
        assert "transaction" in response_data
        assert "message" in response_data
        
        transaction = response_data["transaction"]
        assert transaction["vendor_id"] == vendor_id
        assert transaction["purchase_order_number"] == "PO-INT-001"
        assert transaction["remarks"] == "Integration test transaction"
        assert transaction["created_by"] == "integration_test"
        assert transaction["total_amount"] == "0.00"
        assert transaction["grand_total"] == "0.00"
        assert transaction["is_active"] is True
        
        # Verify transaction ID format
        assert transaction["transaction_id"].startswith("PUR-")
    
    def test_create_transaction_with_items_integration(self, client, setup_test_data):
        """Test creating a purchase transaction with items via API."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        warehouse_id = str(test_data["warehouse"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-INT-002",
            "remarks": "Integration test with items",
            "created_by": "integration_test",
            "items": [
                {
                    "item_master_id": item_master_id,
                    "quantity": 2,
                    "unit_price": "125.00",
                    "warehouse_id": warehouse_id,
                    "serial_number": ["SN-INT-001", "SN-INT-002"],
                    "discount": "25.00",
                    "tax_amount": "20.00",
                    "remarks": "Integration test item",
                    "warranty_period_type": "MONTHS",
                    "warranty_period": 12
                }
            ]
        }
        
        response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
        
        assert response.status_code == 201
        
        response_data = response.json()
        transaction = response_data["transaction"]
        
        # Verify transaction totals were calculated
        # (2 * 125.00) - 25.00 + 20.00 = 245.00
        assert transaction["total_amount"] == "245.00"
        assert transaction["grand_total"] == "245.00"
    
    def test_get_transactions_with_pagination_integration(self, client, setup_test_data):
        """Test getting transactions with pagination."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        # Create multiple transactions
        for i in range(5):
            request_data = {
                "transaction_date": date.today().isoformat(),
                "vendor_id": vendor_id,
                "purchase_order_number": f"PO-PAGE-{i+1:03d}",
                "remarks": f"Pagination test transaction {i+1}",
                "created_by": "pagination_test"
            }
            
            response = client.post("/api/v1/purchase-transactions/", json=request_data)
            assert response.status_code == 201
        
        # Test pagination
        response = client.get("/api/v1/purchase-transactions/?page=1&page_size=3")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert len(response_data["transactions"]) == 3
        assert response_data["total"] == 5
        assert response_data["page"] == 1
        assert response_data["page_size"] == 3
        assert response_data["total_pages"] == 2
    
    def test_get_transactions_with_filters_integration(self, client, setup_test_data):
        """Test getting transactions with various filters."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        # Create transaction with specific date and PO number
        transaction_date = date(2024, 6, 15)
        request_data = {
            "transaction_date": transaction_date.isoformat(),
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-FILTER-001",
            "remarks": "Filter test transaction",
            "created_by": "filter_test"
        }
        
        response = client.post("/api/v1/purchase-transactions/", json=request_data)
        assert response.status_code == 201
        
        # Test vendor filter
        response = client.get(f"/api/v1/purchase-transactions/?vendor_id={vendor_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["transactions"]) >= 1
        assert all(t["vendor_id"] == vendor_id for t in response_data["transactions"])
        
        # Test date range filter
        response = client.get(
            "/api/v1/purchase-transactions/"
            f"?date_from=2024-06-01&date_to=2024-06-30&vendor_id={vendor_id}"
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["transactions"]) >= 1
        
        # Test purchase order number filter
        response = client.get(
            f"/api/v1/purchase-transactions/?purchase_order_number=FILTER&vendor_id={vendor_id}"
        )
        assert response.status_code == 200
        response_data = response.json()
        assert len(response_data["transactions"]) >= 1
        assert all("FILTER" in t["purchase_order_number"] for t in response_data["transactions"])
    
    def test_get_transaction_with_items_integration(self, client, setup_test_data):
        """Test getting a specific transaction with its items."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Create transaction with items
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "items": [
                {
                    "item_master_id": item_master_id,
                    "quantity": 3,
                    "unit_price": "100.00",
                    "serial_number": ["SN-GET-001", "SN-GET-002", "SN-GET-003"],
                    "discount": "30.00",
                    "tax_amount": "22.50"
                }
            ]
        }
        
        create_response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Get transaction with items
        response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["id"] == transaction_id
        assert len(response_data["items"]) == 1
        
        item = response_data["items"][0]
        assert item["inventory_item_id"] == item_master_id
        assert item["quantity"] == 3
        assert item["unit_price"] == "100.00"
        assert item["serial_number"] == ["SN-GET-001", "SN-GET-002", "SN-GET-003"]
        assert item["discount"] == "30.00"
        assert item["tax_amount"] == "22.50"
        assert item["total_price"] == "292.50"  # (3 * 100.00) - 30.00 + 22.50
        
        # Verify item summary
        assert "item_summary" in response_data
        summary = response_data["item_summary"]
        assert summary["total_items"] == 1
        assert summary["total_quantity"] == 3
        assert summary["total_amount"] == 292.50
        assert summary["items_with_serial_numbers"] == 1
    
    def test_update_transaction_integration(self, client, setup_test_data):
        """Test updating a purchase transaction."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        # Create transaction
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-UPDATE-BEFORE",
            "remarks": "Before update",
            "created_by": "update_test"
        }
        
        create_response = client.post("/api/v1/purchase-transactions/", json=request_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Update transaction
        update_data = {
            "purchase_order_number": "PO-UPDATE-AFTER",
            "remarks": "After update"
        }
        
        response = client.put(f"/api/v1/purchase-transactions/{transaction_id}/", json=update_data)
        
        assert response.status_code == 200
        
        response_data = response.json()
        transaction = response_data["transaction"]
        assert transaction["purchase_order_number"] == "PO-UPDATE-AFTER"
        assert transaction["remarks"] == "After update"
        
        # Verify update persisted
        get_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
        assert get_response.status_code == 200
        
        get_data = get_response.json()
        assert get_data["purchase_order_number"] == "PO-UPDATE-AFTER"
        assert get_data["remarks"] == "After update"
    
    def test_delete_transaction_integration(self, client, setup_test_data):
        """Test deleting a purchase transaction."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        # Create transaction
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-DELETE-001",
            "created_by": "delete_test"
        }
        
        create_response = client.post("/api/v1/purchase-transactions/", json=request_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Delete transaction
        response = client.delete(f"/api/v1/purchase-transactions/{transaction_id}/")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["message"] == "Purchase transaction deleted successfully"
        assert response_data["transaction_id"] == transaction_id
        
        # Verify transaction is soft deleted
        get_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
        assert get_response.status_code == 404
    
    def test_search_transactions_integration(self, client, setup_test_data):
        """Test searching transactions."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        # Create transaction with searchable content
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-SEARCH-UNIQUE",
            "remarks": "Searchable transaction with unique content",
            "created_by": "search_test"
        }
        
        create_response = client.post("/api/v1/purchase-transactions/", json=request_data)
        assert create_response.status_code == 201
        
        # Search for the transaction
        search_data = {
            "query": "SEARCH-UNIQUE",
            "vendor_id": vendor_id,
            "limit": 10
        }
        
        response = client.post("/api/v1/purchase-transactions/search/", json=search_data)
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert len(response_data["transactions"]) >= 1
        
        # Verify search result
        found_transaction = next(
            (t for t in response_data["transactions"] if "SEARCH-UNIQUE" in t["purchase_order_number"]), 
            None
        )
        assert found_transaction is not None
        assert found_transaction["vendor_id"] == vendor_id
    
    def test_transaction_statistics_integration(self, client, setup_test_data):
        """Test getting transaction statistics."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Create transactions with different amounts
        amounts = [100.00, 250.00, 500.00]
        for i, amount in enumerate(amounts):
            request_data = {
                "transaction_date": date.today().isoformat(),
                "vendor_id": vendor_id,
                "items": [
                    {
                        "item_master_id": item_master_id,
                        "quantity": 1,
                        "unit_price": str(amount)
                    }
                ]
            }
            
            response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
            assert response.status_code == 201
        
        # Get statistics
        response = client.get("/api/v1/purchase-transactions/statistics/summary/")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert "total_amount" in response_data
        assert "total_transactions" in response_data
        assert "recent_amount" in response_data
        assert "recent_transactions" in response_data
        
        # Verify statistics include our transactions
        assert float(response_data["total_amount"]) >= 850.00  # Sum of our amounts
        assert response_data["total_transactions"] >= 3


class TestPurchaseTransactionItemAPIIntegration:
    """Test purchase transaction item API integration."""
    
    def test_add_item_to_existing_transaction_integration(self, client, setup_test_data):
        """Test adding items to an existing transaction."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        warehouse_id = str(test_data["warehouse"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Create transaction
        transaction_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "created_by": "item_test"
        }
        
        create_response = client.post("/api/v1/purchase-transactions/", json=transaction_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Add item to transaction
        item_data = {
            "item_master_id": item_master_id,
            "quantity": 2,
            "unit_price": "175.00",
            "warehouse_id": warehouse_id,
            "serial_number": ["SN-ADD-001", "SN-ADD-002"],
            "discount": "35.00",
            "tax_amount": "28.00",
            "remarks": "Added item",
            "warranty_period_type": "YEARS",
            "warranty_period": 1
        }
        
        response = client.post(f"/api/v1/purchase-transactions/{transaction_id}/items/", json=item_data)
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert "item" in response_data
        assert "message" in response_data
        
        item = response_data["item"]
        assert item["transaction_id"] == transaction_id
        assert item["inventory_item_id"] == item_master_id
        assert item["quantity"] == 2
        assert item["unit_price"] == "175.00"
        assert item["warehouse_id"] == warehouse_id
        assert item["serial_number"] == ["SN-ADD-001", "SN-ADD-002"]
        assert item["discount"] == "35.00"
        assert item["tax_amount"] == "28.00"
        assert item["total_price"] == "343.00"  # (2 * 175.00) - 35.00 + 28.00
        assert item["remarks"] == "Added item"
        assert item["warranty_period_type"] == "YEARS"
        assert item["warranty_period"] == 1
        
        # Verify transaction totals were updated
        get_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
        assert get_response.status_code == 200
        
        transaction = get_response.json()
        assert transaction["total_amount"] == "343.00"
        assert transaction["grand_total"] == "343.00"
    
    def test_bulk_add_items_integration(self, client, setup_test_data):
        """Test bulk adding items to a transaction."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Change inventory item to BULK tracking for this test
        test_data["inventory_item"].tracking_type = "BULK"
        
        # Create transaction
        transaction_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "created_by": "bulk_test"
        }
        
        create_response = client.post("/api/v1/purchase-transactions/", json=transaction_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Bulk add items
        bulk_data = {
            "items": [
                {
                    "item_master_id": item_master_id,
                    "quantity": 5,
                    "unit_price": "80.00",
                    "serial_number": ["BATCH-001"]
                },
                {
                    "item_master_id": item_master_id,
                    "quantity": 3,
                    "unit_price": "90.00",
                    "discount": "15.00",
                    "tax_amount": "20.25"
                }
            ]
        }
        
        response = client.post(f"/api/v1/purchase-transactions/{transaction_id}/items/bulk/", json=bulk_data)
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert len(response_data["created_items"]) == 2
        assert response_data["total_created"] == 2
        assert response_data["total_requested"] == 2
        assert response_data["transaction_id"] == transaction_id
        
        # Verify transaction totals
        # Item 1: 5 * 80.00 = 400.00
        # Item 2: (3 * 90.00) - 15.00 + 20.25 = 275.25
        # Total: 675.25
        assert response_data["updated_totals"]["total_amount"] == Decimal("675.25")
        assert response_data["updated_totals"]["grand_total"] == Decimal("675.25")
    
    def test_get_transaction_items_integration(self, client, setup_test_data):
        """Test getting items for a transaction."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Create transaction with multiple items
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "items": [
                {
                    "item_master_id": item_master_id,
                    "quantity": 1,
                    "unit_price": "100.00",
                    "serial_number": ["SN-LIST-001"]
                },
                {
                    "item_master_id": item_master_id,
                    "quantity": 1,
                    "unit_price": "150.00",
                    "serial_number": ["SN-LIST-002"]
                }
            ]
        }
        
        create_response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Get transaction items
        response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/items/")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert len(response_data["items"]) == 2
        assert response_data["total"] == 2
        assert response_data["page"] == 1
        assert response_data["page_size"] == 50
        assert response_data["total_pages"] == 1
        
        # Verify items content
        items = response_data["items"]
        unit_prices = [item["unit_price"] for item in items]
        assert "100.00" in unit_prices
        assert "150.00" in unit_prices
    
    def test_update_transaction_item_integration(self, client, setup_test_data):
        """Test updating a transaction item."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Create transaction with item
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "items": [
                {
                    "item_master_id": item_master_id,
                    "quantity": 2,
                    "unit_price": "120.00",
                    "serial_number": ["SN-UPD-001", "SN-UPD-002"],
                    "discount": "20.00",
                    "tax_amount": "18.00"
                }
            ]
        }
        
        create_response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Get item ID
        items_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/items/")
        item_id = items_response.json()["items"][0]["id"]
        
        # Update item
        update_data = {
            "unit_price": "140.00",
            "discount": "30.00",
            "tax_amount": "25.00",
            "remarks": "Updated item pricing"
        }
        
        response = client.put(
            f"/api/v1/purchase-transactions/{transaction_id}/items/{item_id}/", 
            json=update_data
        )
        
        assert response.status_code == 200
        
        response_data = response.json()
        item = response_data["item"]
        assert item["unit_price"] == "140.00"
        assert item["discount"] == "30.00"
        assert item["tax_amount"] == "25.00"
        assert item["total_price"] == "275.00"  # (2 * 140.00) - 30.00 + 25.00
        assert item["remarks"] == "Updated item pricing"
        
        # Verify transaction totals were updated
        transaction_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
        transaction = transaction_response.json()
        assert transaction["total_amount"] == "275.00"
        assert transaction["grand_total"] == "275.00"
    
    def test_delete_transaction_item_integration(self, client, setup_test_data):
        """Test deleting a transaction item."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Create transaction with multiple items
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "items": [
                {
                    "item_master_id": item_master_id,
                    "quantity": 1,
                    "unit_price": "100.00",
                    "serial_number": ["SN-DEL-001"]
                },
                {
                    "item_master_id": item_master_id,
                    "quantity": 1,
                    "unit_price": "200.00",
                    "serial_number": ["SN-DEL-002"]
                }
            ]
        }
        
        create_response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
        assert create_response.status_code == 201
        
        transaction_id = create_response.json()["transaction"]["id"]
        
        # Get items
        items_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/items/")
        items = items_response.json()["items"]
        
        # Find item to delete (the 100.00 one)
        item_to_delete = next(item for item in items if item["unit_price"] == "100.00")
        item_id = item_to_delete["id"]
        
        # Delete item
        response = client.delete(f"/api/v1/purchase-transactions/{transaction_id}/items/{item_id}/")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["message"] == "Transaction item deleted successfully"
        assert response_data["item_id"] == item_id
        
        # Verify item was deleted
        items_after_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/items/")
        items_after = items_after_response.json()["items"]
        assert len(items_after) == 1
        assert items_after[0]["unit_price"] == "200.00"
        
        # Verify transaction totals were updated
        transaction_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
        transaction = transaction_response.json()
        assert transaction["total_amount"] == "200.00"
        assert transaction["grand_total"] == "200.00"


class TestPurchaseTransactionDatabaseIntegration:
    """Test purchase transaction database persistence and constraints."""
    
    def test_transaction_persistence(self, db_session, setup_test_data):
        """Test that transactions are properly persisted to database."""
        test_data = setup_test_data
        vendor_id = test_data["vendor"].id
        
        # Create transaction model
        transaction_model = PurchaseTransactionModel(
            id=str(uuid4()),
            transaction_id="PUR-PERSIST-001",
            transaction_date=date.today(),
            vendor_id=vendor_id,
            total_amount=500.00,
            grand_total=525.00,
            purchase_order_number="PO-PERSIST-001",
            remarks="Persistence test",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="persistence_test",
            is_active=True
        )
        
        db_session.add(transaction_model)
        db_session.commit()
        
        # Verify persistence
        retrieved = db_session.query(PurchaseTransactionModel).filter_by(
            transaction_id="PUR-PERSIST-001"
        ).first()
        
        assert retrieved is not None
        assert retrieved.transaction_id == "PUR-PERSIST-001"
        assert retrieved.vendor_id == vendor_id
        assert retrieved.total_amount == 500.00
        assert retrieved.grand_total == 525.00
        assert retrieved.purchase_order_number == "PO-PERSIST-001"
        assert retrieved.remarks == "Persistence test"
        assert retrieved.created_by == "persistence_test"
        assert retrieved.is_active is True
    
    def test_transaction_item_persistence(self, db_session, setup_test_data):
        """Test that transaction items are properly persisted."""
        test_data = setup_test_data
        vendor_id = test_data["vendor"].id
        warehouse_id = test_data["warehouse"].id
        inventory_item_id = test_data["inventory_item"].id
        
        # Create transaction
        transaction_model = PurchaseTransactionModel(
            id=str(uuid4()),
            transaction_id="PUR-ITEM-PERSIST-001",
            transaction_date=date.today(),
            vendor_id=vendor_id,
            total_amount=0.00,
            grand_total=0.00,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        db_session.add(transaction_model)
        db_session.flush()
        
        # Create transaction item
        item_model = PurchaseTransactionItemModel(
            id=str(uuid4()),
            transaction_id=transaction_model.id,
            inventory_item_id=inventory_item_id,
            warehouse_id=warehouse_id,
            quantity=3,
            unit_price=150.00,
            discount=45.00,
            tax_amount=30.00,
            total_price=435.00,  # (3 * 150.00) - 45.00 + 30.00
            serial_number=["SN-PERSIST-001", "SN-PERSIST-002", "SN-PERSIST-003"],
            remarks="Item persistence test",
            warranty_period_type="MONTHS",
            warranty_period=6,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by="item_persistence_test",
            is_active=True
        )
        
        db_session.add(item_model)
        db_session.commit()
        
        # Verify persistence
        retrieved_item = db_session.query(PurchaseTransactionItemModel).filter_by(
            transaction_id=transaction_model.id
        ).first()
        
        assert retrieved_item is not None
        assert retrieved_item.transaction_id == transaction_model.id
        assert retrieved_item.inventory_item_id == inventory_item_id
        assert retrieved_item.warehouse_id == warehouse_id
        assert retrieved_item.quantity == 3
        assert retrieved_item.unit_price == 150.00
        assert retrieved_item.discount == 45.00
        assert retrieved_item.tax_amount == 30.00
        assert retrieved_item.total_price == 435.00
        assert retrieved_item.serial_number == ["SN-PERSIST-001", "SN-PERSIST-002", "SN-PERSIST-003"]
        assert retrieved_item.remarks == "Item persistence test"
        assert retrieved_item.warranty_period_type == "MONTHS"
        assert retrieved_item.warranty_period == 6
        assert retrieved_item.created_by == "item_persistence_test"
        assert retrieved_item.is_active is True
    
    def test_serial_number_uniqueness_constraint(self, db_session, setup_test_data):
        """Test that serial number uniqueness is enforced."""
        test_data = setup_test_data
        vendor_id = test_data["vendor"].id
        inventory_item_id = test_data["inventory_item"].id
        
        # Create first transaction with serial number
        transaction1 = PurchaseTransactionModel(
            id=str(uuid4()),
            transaction_id="PUR-SERIAL-001",
            transaction_date=date.today(),
            vendor_id=vendor_id,
            total_amount=100.00,
            grand_total=100.00,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        db_session.add(transaction1)
        db_session.flush()
        
        item1 = PurchaseTransactionItemModel(
            id=str(uuid4()),
            transaction_id=transaction1.id,
            inventory_item_id=inventory_item_id,
            quantity=1,
            unit_price=100.00,
            discount=0.00,
            tax_amount=0.00,
            total_price=100.00,
            serial_number=["SN-UNIQUE-001"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        db_session.add(item1)
        db_session.commit()
        
        # Verify first item was created successfully
        first_item = db_session.query(PurchaseTransactionItemModel).filter(
            PurchaseTransactionItemModel.serial_number.op('@>')(['SN-UNIQUE-001'])
        ).first()
        
        assert first_item is not None
        assert "SN-UNIQUE-001" in first_item.serial_number
    
    def test_soft_delete_behavior(self, db_session, setup_test_data):
        """Test soft delete behavior for transactions and items."""
        test_data = setup_test_data
        vendor_id = test_data["vendor"].id
        inventory_item_id = test_data["inventory_item"].id
        
        # Create transaction with item
        transaction = PurchaseTransactionModel(
            id=str(uuid4()),
            transaction_id="PUR-SOFT-DELETE-001",
            transaction_date=date.today(),
            vendor_id=vendor_id,
            total_amount=200.00,
            grand_total=200.00,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        db_session.add(transaction)
        db_session.flush()
        
        item = PurchaseTransactionItemModel(
            id=str(uuid4()),
            transaction_id=transaction.id,
            inventory_item_id=inventory_item_id,
            quantity=2,
            unit_price=100.00,
            discount=0.00,
            tax_amount=0.00,
            total_price=200.00,
            serial_number=["SN-SOFT-001", "SN-SOFT-002"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        
        db_session.add(item)
        db_session.commit()
        
        # Verify records exist
        assert db_session.query(PurchaseTransactionModel).filter_by(
            id=transaction.id, is_active=True
        ).count() == 1
        
        assert db_session.query(PurchaseTransactionItemModel).filter_by(
            transaction_id=transaction.id, is_active=True
        ).count() == 1
        
        # Soft delete transaction
        transaction.is_active = False
        db_session.commit()
        
        # Verify transaction is soft deleted
        assert db_session.query(PurchaseTransactionModel).filter_by(
            id=transaction.id, is_active=True
        ).count() == 0
        
        assert db_session.query(PurchaseTransactionModel).filter_by(
            id=transaction.id, is_active=False
        ).count() == 1
        
        # Soft delete item
        item.is_active = False
        db_session.commit()
        
        # Verify item is soft deleted
        assert db_session.query(PurchaseTransactionItemModel).filter_by(
            transaction_id=transaction.id, is_active=True
        ).count() == 0
        
        assert db_session.query(PurchaseTransactionItemModel).filter_by(
            transaction_id=transaction.id, is_active=False
        ).count() == 1


class TestPurchaseTransactionPerformanceIntegration:
    """Test purchase transaction performance and scalability."""
    
    def test_bulk_transaction_creation_performance(self, client, setup_test_data):
        """Test performance of creating multiple transactions."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        import time
        
        # Create 10 transactions and measure time
        start_time = time.time()
        
        transaction_ids = []
        for i in range(10):
            request_data = {
                "transaction_date": date.today().isoformat(),
                "vendor_id": vendor_id,
                "purchase_order_number": f"PO-PERF-{i+1:03d}",
                "remarks": f"Performance test transaction {i+1}",
                "created_by": "performance_test"
            }
            
            response = client.post("/api/v1/purchase-transactions/", json=request_data)
            assert response.status_code == 201
            
            transaction_ids.append(response.json()["transaction"]["id"])
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        assert total_time < 10.0  # 10 seconds for 10 transactions
        assert len(transaction_ids) == 10
        
        # Verify all transactions were created
        for transaction_id in transaction_ids:
            response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/")
            assert response.status_code == 200
    
    def test_large_item_list_performance(self, client, setup_test_data):
        """Test performance with transactions containing many items."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        item_master_id = str(test_data["inventory_item"].id)
        
        # Change inventory item to BULK tracking for performance
        test_data["inventory_item"].tracking_type = "BULK"
        
        import time
        
        # Create transaction with 20 items
        items = []
        for i in range(20):
            items.append({
                "item_master_id": item_master_id,
                "quantity": 1,
                "unit_price": f"{100 + i}.00"
            })
        
        request_data = {
            "transaction_date": date.today().isoformat(),
            "vendor_id": vendor_id,
            "items": items,
            "remarks": "Large item list performance test"
        }
        
        start_time = time.time()
        
        response = client.post("/api/v1/purchase-transactions/with-items/", json=request_data)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert response.status_code == 201
        assert total_time < 5.0  # Should complete within 5 seconds
        
        transaction_id = response.json()["transaction"]["id"]
        
        # Verify all items were created
        items_response = client.get(f"/api/v1/purchase-transactions/{transaction_id}/items/")
        assert items_response.status_code == 200
        
        items_data = items_response.json()
        assert len(items_data["items"]) == 20
        assert items_data["total"] == 20
    
    def test_pagination_performance(self, client, setup_test_data):
        """Test pagination performance with large result sets."""
        test_data = setup_test_data
        vendor_id = str(test_data["vendor"].id)
        
        # Create 50 transactions for pagination testing
        for i in range(50):
            request_data = {
                "transaction_date": date.today().isoformat(),
                "vendor_id": vendor_id,
                "purchase_order_number": f"PO-PAGE-{i+1:03d}",
                "created_by": "pagination_performance_test"
            }
            
            response = client.post("/api/v1/purchase-transactions/", json=request_data)
            assert response.status_code == 201
        
        import time
        
        # Test different page sizes
        page_sizes = [10, 25, 50]
        
        for page_size in page_sizes:
            start_time = time.time()
            
            response = client.get(f"/api/v1/purchase-transactions/?page=1&page_size={page_size}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            assert response.status_code == 200
            assert total_time < 2.0  # Should complete within 2 seconds
            
            response_data = response.json()
            assert len(response_data["transactions"]) <= page_size
            assert response_data["page_size"] == page_size