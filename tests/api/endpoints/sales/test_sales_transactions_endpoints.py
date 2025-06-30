"""API tests for Sales Transactions endpoints"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from src.infrastructure.repositories.inventory_item_master_repository_impl import SQLAlchemyInventoryItemMasterRepository
from src.infrastructure.repositories.warehouse_repository_impl import SQLAlchemyWarehouseRepository
from src.infrastructure.repositories.item_category_repository_impl import SQLAlchemyItemCategoryRepository
from src.infrastructure.repositories.unit_of_measurement_repository_impl import SQLAlchemyUnitOfMeasurementRepository
from src.domain.entities.customer import Customer
from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.domain.entities.warehouse import Warehouse
from src.domain.entities.item_category import ItemCategory, ItemSubCategory
from src.domain.entities.unit_of_measurement import UnitOfMeasurement


@pytest.mark.api
class TestSalesTransactionsEndpoints:
    """Test suite for sales transactions API endpoints"""
    
    @pytest.fixture
    async def test_customer(self, async_session: AsyncSession):
        """Create a test customer"""
        repo = SQLAlchemyCustomerRepository(async_session)
        customer = Customer(
            name="API Test Customer",
            email=f"api_test_{uuid4().hex[:8]}@example.com",
            address="123 API Test St",
            city="Test City",
            credit_limit=Decimal("5000.00")
        )
        return await repo.save(customer)
    
    @pytest.fixture
    async def test_warehouse(self, async_session: AsyncSession):
        """Create a test warehouse"""
        repo = SQLAlchemyWarehouseRepository(async_session)
        warehouse = Warehouse(
            name="API Test Warehouse",
            label="API_TEST_WH",
            remarks="Test warehouse for API"
        )
        return await repo.save(warehouse)
    
    @pytest.fixture
    async def test_category(self, async_session: AsyncSession):
        """Create test category and subcategory"""
        repo = SQLAlchemyItemCategoryRepository(async_session)
        category = ItemCategory(
            name="API Test Category",
            abbreviation="APICAT"
        )
        saved_category = await repo.save(category)
        
        subcategory = ItemSubCategory(
            name="API Test Subcategory",
            abbreviation="APISUB",
            item_category_id=saved_category.id
        )
        saved_subcategory = await repo.save_subcategory(subcategory)
        
        return saved_category, saved_subcategory
    
    @pytest.fixture
    async def test_unit(self, async_session: AsyncSession):
        """Create a test unit of measurement"""
        repo = SQLAlchemyUnitOfMeasurementRepository(async_session)
        unit = UnitOfMeasurement(
            name="Piece",
            abbreviation="PC"
        )
        return await repo.save(unit)
    
    @pytest.fixture
    async def test_inventory_items(self, async_session: AsyncSession, test_category, test_unit):
        """Create test inventory items"""
        repo = SQLAlchemyInventoryItemMasterRepository(async_session)
        _, subcategory = test_category
        
        items = []
        for i in range(2):
            item = InventoryItemMaster(
                name=f"API Test Item {i+1}",
                sku=f"API-TEST-{i+1}",
                description=f"Test item {i+1} for API tests",
                item_sub_category_id=subcategory.id,
                unit_of_measurement_id=test_unit.id,
                tracking_type="INDIVIDUAL" if i == 0 else "BULK",
                quantity=10,
                brand="TestBrand",
                renting_period=7
            )
            saved = await repo.save(item)
            items.append(saved)
        
        return items
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_success(self, async_client: AsyncClient, test_customer,
                                                   test_warehouse, test_inventory_items):
        """Test successful sales transaction creation"""
        item1, item2 = test_inventory_items
        
        request_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 2,
                    "unit_price": 100.00,
                    "discount_percentage": 5.0,
                    "tax_rate": 10.0,
                    "serial_numbers": ["SN001", "SN002"]
                },
                {
                    "inventory_item_master_id": str(item2.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 5,
                    "unit_price": 50.00,
                    "tax_rate": 8.0
                }
            ],
            "shipping_amount": 25.00,
            "payment_terms": "NET_30",
            "shipping_address": "789 Delivery St, Test City",
            "billing_address": "456 Invoice Ave, Test City",
            "purchase_order_number": "PO-CUST-12345",
            "notes": "Please handle with care",
            "customer_notes": "Leave at reception"
        }
        
        response = await async_client.post("/api/v1/sales/transactions/", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["customer_id"] == str(test_customer.id)
        assert data["payment_terms"] == "NET_30"
        assert data["status"] == "DRAFT"
        assert data["payment_status"] == "PENDING"
        assert len(data["items"]) == 2
        assert data["shipping_amount"] == "25.00"
        assert "transaction_id" in data
        assert data["transaction_id"].startswith("SO-")
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_invalid_customer(self, async_client: AsyncClient,
                                                           test_warehouse, test_inventory_items):
        """Test transaction creation with invalid customer"""
        item1, _ = test_inventory_items
        
        request_data = {
            "customer_id": str(uuid4()),  # Non-existent customer
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "payment_terms": "NET_30"
        }
        
        response = await async_client.post("/api/v1/sales/transactions/", json=request_data)
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction_empty_items(self, async_client: AsyncClient, test_customer):
        """Test transaction creation with no items"""
        request_data = {
            "customer_id": str(test_customer.id),
            "items": [],
            "payment_terms": "NET_30"
        }
        
        response = await async_client.post("/api/v1/sales/transactions/", json=request_data)
        
        assert response.status_code == 400
        assert "at least one item" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_sales_transaction(self, async_client: AsyncClient, test_customer,
                                       test_warehouse, test_inventory_items):
        """Test retrieving a sales transaction"""
        # First create a transaction
        item1, _ = test_inventory_items
        create_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 1,
                    "unit_price": 150.00,
                    "tax_rate": 10.0
                }
            ],
            "payment_terms": "IMMEDIATE"
        }
        
        create_response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
        assert create_response.status_code == 201
        transaction_id = create_response.json()["id"]
        
        # Get the transaction
        response = await async_client.get(f"/api/v1/sales/transactions/{transaction_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == transaction_id
        assert data["customer"]["id"] == str(test_customer.id)
        assert data["customer"]["name"] == test_customer.name
        assert len(data["items"]) == 1
        assert data["items"][0]["inventory_item"]["id"] == str(item1.id)
    
    @pytest.mark.asyncio
    async def test_get_sales_transaction_not_found(self, async_client: AsyncClient):
        """Test retrieving non-existent transaction"""
        response = await async_client.get(f"/api/v1/sales/transactions/{uuid4()}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_list_sales_transactions(self, async_client: AsyncClient, test_customer,
                                          test_warehouse, test_inventory_items):
        """Test listing sales transactions"""
        # Create multiple transactions
        item1, _ = test_inventory_items
        for i in range(3):
            create_data = {
                "customer_id": str(test_customer.id),
                "items": [
                    {
                        "inventory_item_master_id": str(item1.id),
                        "warehouse_id": str(test_warehouse.id),
                        "quantity": 1,
                        "unit_price": 100.00 * (i + 1)
                    }
                ],
                "payment_terms": "NET_30"
            }
            response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
            assert response.status_code == 201
        
        # List transactions
        response = await async_client.get("/api/v1/sales/transactions/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) >= 3
        # Verify they're sorted by most recent first
        dates = [datetime.fromisoformat(t["order_date"].replace("Z", "+00:00")) for t in data]
        assert dates == sorted(dates, reverse=True)
    
    @pytest.mark.asyncio
    async def test_list_sales_transactions_with_filters(self, async_client: AsyncClient, test_customer,
                                                       test_warehouse, test_inventory_items):
        """Test listing transactions with filters"""
        # Create transactions with different statuses
        item1, _ = test_inventory_items
        
        # Create and confirm a transaction
        create_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 1,
                    "unit_price": 200.00
                }
            ],
            "payment_terms": "NET_30"
        }
        
        create_response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
        transaction_id = create_response.json()["id"]
        
        # Confirm the transaction
        await async_client.post(f"/api/v1/sales/transactions/{transaction_id}/confirm")
        
        # Test customer filter
        response = await async_client.get(
            f"/api/v1/sales/transactions/?customer_id={test_customer.id}"
        )
        assert response.status_code == 200
        assert all(t["customer_id"] == str(test_customer.id) for t in response.json())
        
        # Test status filter
        response = await async_client.get("/api/v1/sales/transactions/?status=CONFIRMED")
        assert response.status_code == 200
        confirmed = [t for t in response.json() if t["status"] == "CONFIRMED"]
        assert len(confirmed) >= 1
    
    @pytest.mark.asyncio
    async def test_update_sales_transaction(self, async_client: AsyncClient, test_customer,
                                           test_warehouse, test_inventory_items):
        """Test updating a sales transaction"""
        # Create a transaction
        item1, _ = test_inventory_items
        create_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "payment_terms": "NET_30"
        }
        
        create_response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
        transaction_id = create_response.json()["id"]
        
        # Update transaction
        update_data = {
            "shipping_address": "123 New Shipping Address",
            "notes": "Updated internal notes",
            "customer_notes": "Updated customer notes"
        }
        
        response = await async_client.patch(
            f"/api/v1/sales/transactions/{transaction_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["shipping_address"] == "123 New Shipping Address"
        assert data["notes"] == "Updated internal notes"
        assert data["customer_notes"] == "Updated customer notes"
    
    @pytest.mark.asyncio
    async def test_confirm_sales_transaction(self, async_client: AsyncClient, test_customer,
                                            test_warehouse, test_inventory_items):
        """Test confirming a sales transaction"""
        # Create a draft transaction
        item1, _ = test_inventory_items
        create_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 2,
                    "unit_price": 75.00
                }
            ],
            "payment_terms": "NET_15"
        }
        
        create_response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
        transaction_id = create_response.json()["id"]
        
        # Confirm transaction
        response = await async_client.post(f"/api/v1/sales/transactions/{transaction_id}/confirm")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "CONFIRMED"
        assert data["payment_due_date"] is not None
    
    @pytest.mark.asyncio
    async def test_cancel_sales_transaction(self, async_client: AsyncClient, test_customer,
                                          test_warehouse, test_inventory_items):
        """Test cancelling a sales transaction"""
        # Create a transaction
        item1, _ = test_inventory_items
        create_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 1,
                    "unit_price": 100.00
                }
            ],
            "payment_terms": "COD"
        }
        
        create_response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
        transaction_id = create_response.json()["id"]
        
        # Cancel transaction
        response = await async_client.post(
            f"/api/v1/sales/transactions/{transaction_id}/cancel",
            json={"reason": "Customer cancelled order"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "CANCELLED"
    
    @pytest.mark.asyncio
    async def test_process_payment(self, async_client: AsyncClient, test_customer,
                                 test_warehouse, test_inventory_items):
        """Test processing payment for a transaction"""
        # Create and confirm a transaction
        item1, _ = test_inventory_items
        create_data = {
            "customer_id": str(test_customer.id),
            "items": [
                {
                    "inventory_item_master_id": str(item1.id),
                    "warehouse_id": str(test_warehouse.id),
                    "quantity": 3,
                    "unit_price": 100.00,
                    "tax_rate": 10.0
                }
            ],
            "payment_terms": "NET_30"
        }
        
        create_response = await async_client.post("/api/v1/sales/transactions/", json=create_data)
        transaction_id = create_response.json()["id"]
        grand_total = Decimal(create_response.json()["grand_total"])
        
        # Confirm first
        await async_client.post(f"/api/v1/sales/transactions/{transaction_id}/confirm")
        
        # Process partial payment
        payment_data = {
            "payment_amount": float(grand_total / 2),
            "payment_method": "CREDIT_CARD",
            "reference_number": "PAY-12345",
            "notes": "First installment"
        }
        
        response = await async_client.post(
            f"/api/v1/sales/transactions/{transaction_id}/payment",
            json=payment_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["payment_status"] == "PARTIAL"
        assert Decimal(data["amount_paid"]) == grand_total / 2
        assert Decimal(data["balance_due"]) == grand_total / 2
    
    @pytest.mark.asyncio
    async def test_get_overdue_transactions(self, async_client: AsyncClient):
        """Test retrieving overdue transactions"""
        response = await async_client.get("/api/v1/sales/transactions/overdue")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned transactions should be overdue
        for transaction in data:
            assert transaction["payment_status"] in ["PENDING", "PARTIAL", "OVERDUE"]
            if transaction["payment_due_date"]:
                due_date = datetime.fromisoformat(transaction["payment_due_date"])
                assert due_date.date() < datetime.now().date()
    
    @pytest.mark.asyncio
    async def test_get_sales_summary(self, async_client: AsyncClient):
        """Test getting sales summary"""
        # Get summary for last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        response = await async_client.get(
            f"/api/v1/sales/transactions/summary?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_sales" in data
        assert "total_orders" in data
        assert "paid_amount" in data
        assert "pending_amount" in data
        assert "average_order_value" in data