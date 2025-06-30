"""API tests for Sales Returns endpoints"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from src.infrastructure.repositories.inventory_item_master_repository_impl import SQLAlchemyInventoryItemMasterRepository
from src.infrastructure.repositories.warehouse_repository_impl import SQLAlchemyWarehouseRepository
from src.infrastructure.repositories.sales_transaction_repository_impl import SQLAlchemySalesTransactionRepository
from src.infrastructure.repositories.sales_transaction_item_repository_impl import SQLAlchemySalesTransactionItemRepository
from src.domain.entities.customer import Customer
from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.domain.entities.warehouse import Warehouse
from src.domain.entities.sales import SalesTransaction, SalesTransactionItem
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms


@pytest.mark.api
class TestSalesReturnsEndpoints:
    """Test suite for sales returns API endpoints"""
    
    @pytest.fixture
    async def test_setup(self, async_session: AsyncSession):
        """Create test data setup"""
        # Create customer
        customer_repo = SQLAlchemyCustomerRepository(async_session)
        customer = Customer(
            name="Return Test Customer",
            email=f"return_test_{uuid4().hex[:8]}@example.com",
            address="123 Return St",
            city="Return City"
        )
        saved_customer = await customer_repo.save(customer)
        
        # Create warehouse
        warehouse_repo = SQLAlchemyWarehouseRepository(async_session)
        warehouse = Warehouse(
            name="Return Test Warehouse",
            label="RETURN_WH",
            remarks="Test warehouse for returns"
        )
        saved_warehouse = await warehouse_repo.save(warehouse)
        
        # Create inventory item
        inventory_repo = SQLAlchemyInventoryItemMasterRepository(async_session)
        
        # Need category and unit first (simplified for test)
        from src.infrastructure.repositories.item_category_repository_impl import SQLAlchemyItemCategoryRepository
        from src.infrastructure.repositories.unit_of_measurement_repository_impl import SQLAlchemyUnitOfMeasurementRepository
        from src.domain.entities.item_category import ItemCategory, ItemSubCategory
        from src.domain.entities.unit_of_measurement import UnitOfMeasurement
        
        category_repo = SQLAlchemyItemCategoryRepository(async_session)
        category = ItemCategory(name="Return Test Cat", abbreviation="RETCAT")
        saved_category = await category_repo.save(category)
        
        subcategory = ItemSubCategory(
            name="Return Test Sub",
            abbreviation="RETSUB",
            item_category_id=saved_category.id
        )
        saved_subcategory = await category_repo.save_subcategory(subcategory)
        
        unit_repo = SQLAlchemyUnitOfMeasurementRepository(async_session)
        unit = UnitOfMeasurement(name="Each", abbreviation="EA")
        saved_unit = await unit_repo.save(unit)
        
        inventory_item = InventoryItemMaster(
            name="Return Test Item",
            sku="RET-TEST-001",
            description="Item for return tests",
            item_sub_category_id=saved_subcategory.id,
            unit_of_measurement_id=saved_unit.id,
            tracking_type="INDIVIDUAL",
            quantity=10,
            brand="TestBrand",
            renting_period=7
        )
        saved_item = await inventory_repo.save(inventory_item)
        
        return {
            "customer": saved_customer,
            "warehouse": saved_warehouse,
            "inventory_item": saved_item
        }
    
    @pytest.fixture
    async def test_sales_transaction(self, async_session: AsyncSession, test_setup):
        """Create a delivered sales transaction with items"""
        customer = test_setup["customer"]
        warehouse = test_setup["warehouse"]
        inventory_item = test_setup["inventory_item"]
        
        # Create sales transaction
        sales_repo = SQLAlchemySalesTransactionRepository(async_session)
        transaction = SalesTransaction(
            customer_id=customer.id,
            transaction_id="SO-RETTEST-001",
            order_date=datetime.now() - timedelta(days=5),
            delivery_date=datetime.now() - timedelta(days=2),
            status=SalesStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            payment_terms=PaymentTerms.NET_30,
            subtotal=Decimal("200.00"),
            tax_amount=Decimal("20.00"),
            grand_total=Decimal("220.00"),
            amount_paid=Decimal("220.00")
        )
        saved_transaction = await sales_repo.create(transaction)
        
        # Create transaction items
        item_repo = SQLAlchemySalesTransactionItemRepository(async_session)
        item = SalesTransactionItem(
            transaction_id=saved_transaction.id,
            inventory_item_master_id=inventory_item.id,
            warehouse_id=warehouse.id,
            quantity=2,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00"),
            tax_rate=Decimal("10.00"),
            tax_amount=Decimal("20.00"),
            subtotal=Decimal("200.00"),
            total=Decimal("220.00"),
            serial_numbers=["SN001", "SN002"]
        )
        saved_item = await item_repo.create(item)
        
        return saved_transaction, [saved_item]
    
    @pytest.mark.asyncio
    async def test_create_sales_return_success(self, async_client: AsyncClient, test_sales_transaction):
        """Test successful sales return creation"""
        transaction, items = test_sales_transaction
        
        request_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Customer not satisfied with product quality",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 1,
                    "condition": "GOOD",
                    "serial_numbers": ["SN001"]
                }
            ],
            "restocking_fee": 10.0  # 10% restocking fee
        }
        
        response = await async_client.post("/api/v1/sales/returns/", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["sales_transaction_id"] == str(transaction.id)
        assert data["reason"] == request_data["reason"]
        assert "return_id" in data
        assert data["return_id"].startswith("RET-") or data["return_id"].startswith("SR-")
        assert len(data["items"]) == 1
        assert data["refund_amount"] == "110.00"  # Half of original item total
        assert data["restocking_fee"] == "11.00"  # 10% of refund
        assert data["net_refund_amount"] == "99.00"
        assert data["is_approved"] is False
    
    @pytest.mark.asyncio
    async def test_create_sales_return_invalid_transaction(self, async_client: AsyncClient):
        """Test return creation with invalid transaction"""
        request_data = {
            "sales_transaction_id": str(uuid4()),
            "reason": "Test reason",
            "items": []
        }
        
        response = await async_client.post("/api/v1/sales/returns/", json=request_data)
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_sales_return_wrong_status(self, async_client: AsyncClient, async_session, test_setup):
        """Test return creation for transaction with wrong status"""
        # Create a draft transaction
        sales_repo = SQLAlchemySalesTransactionRepository(async_session)
        transaction = SalesTransaction(
            customer_id=test_setup["customer"].id,
            transaction_id="SO-DRAFT-001",
            order_date=datetime.now(),
            status=SalesStatus.DRAFT
        )
        saved = await sales_repo.create(transaction)
        
        request_data = {
            "sales_transaction_id": str(saved.id),
            "reason": "Cannot return draft order",
            "items": []
        }
        
        response = await async_client.post("/api/v1/sales/returns/", json=request_data)
        
        assert response.status_code == 400
        assert "delivered or shipped" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_sales_return(self, async_client: AsyncClient, test_sales_transaction):
        """Test retrieving a sales return"""
        transaction, items = test_sales_transaction
        
        # Create a return first
        create_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Test return",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 1,
                    "condition": "DAMAGED"
                }
            ],
            "restocking_fee": 0.0
        }
        
        create_response = await async_client.post("/api/v1/sales/returns/", json=create_data)
        return_id = create_response.json()["id"]
        
        # Get the return
        response = await async_client.get(f"/api/v1/sales/returns/{return_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == return_id
        assert data["sales_transaction"]["id"] == str(transaction.id)
        assert len(data["items"]) == 1
        assert data["items"][0]["condition"] == "DAMAGED"
    
    @pytest.mark.asyncio
    async def test_get_sales_return_not_found(self, async_client: AsyncClient):
        """Test retrieving non-existent return"""
        response = await async_client.get(f"/api/v1/sales/returns/{uuid4()}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_list_sales_returns(self, async_client: AsyncClient, test_sales_transaction):
        """Test listing sales returns"""
        transaction, items = test_sales_transaction
        
        # Create multiple returns
        for i in range(3):
            create_data = {
                "sales_transaction_id": str(transaction.id),
                "reason": f"Return reason {i}",
                "items": [
                    {
                        "sales_item_id": str(items[0].id),
                        "quantity": 1,
                        "condition": "GOOD"
                    }
                ],
                "restocking_fee": 5.0 * i
            }
            response = await async_client.post("/api/v1/sales/returns/", json=create_data)
            assert response.status_code == 201
        
        # List returns
        response = await async_client.get("/api/v1/sales/returns/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) >= 3
        # Verify they're sorted by most recent first
        dates = [datetime.fromisoformat(r["return_date"].replace("Z", "+00:00")) for r in data]
        assert dates == sorted(dates, reverse=True)
    
    @pytest.mark.asyncio
    async def test_list_sales_returns_with_filters(self, async_client: AsyncClient, test_sales_transaction):
        """Test listing returns with filters"""
        transaction, items = test_sales_transaction
        
        # Create a return
        create_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Filter test return",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 1,
                    "condition": "GOOD"
                }
            ]
        }
        
        await async_client.post("/api/v1/sales/returns/", json=create_data)
        
        # Test transaction filter
        response = await async_client.get(
            f"/api/v1/sales/returns/?sales_transaction_id={transaction.id}"
        )
        assert response.status_code == 200
        assert all(r["sales_transaction_id"] == str(transaction.id) for r in response.json())
    
    @pytest.mark.asyncio
    async def test_update_sales_return(self, async_client: AsyncClient, test_sales_transaction):
        """Test updating a sales return"""
        transaction, items = test_sales_transaction
        
        # Create a return
        create_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Original reason",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 1,
                    "condition": "GOOD"
                }
            ],
            "restocking_fee": 10.0
        }
        
        create_response = await async_client.post("/api/v1/sales/returns/", json=create_data)
        return_id = create_response.json()["id"]
        
        # Update return
        update_data = {
            "reason": "Updated reason with more details",
            "restocking_fee": 15.0
        }
        
        response = await async_client.patch(
            f"/api/v1/sales/returns/{return_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["reason"] == "Updated reason with more details"
        assert data["restocking_fee"] == "16.50"  # 15% of 110
    
    @pytest.mark.asyncio
    async def test_approve_sales_return(self, async_client: AsyncClient, test_sales_transaction):
        """Test approving a sales return"""
        transaction, items = test_sales_transaction
        
        # Create a return
        create_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "To be approved",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 2,
                    "condition": "GOOD",
                    "serial_numbers": ["SN001", "SN002"]
                }
            ]
        }
        
        create_response = await async_client.post("/api/v1/sales/returns/", json=create_data)
        return_id = create_response.json()["id"]
        
        # Approve return
        approve_data = {
            "notes": "Approved after inspection"
        }
        
        current_user_id = str(uuid4())  # In real app, this would come from auth
        response = await async_client.post(
            f"/api/v1/sales/returns/{return_id}/approve?current_user_id={current_user_id}",
            json=approve_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_approved"] is True
        assert data["approved_by_id"] == current_user_id
        assert "Approval notes:" in data["reason"]
    
    @pytest.mark.asyncio
    async def test_approve_already_approved_return(self, async_client: AsyncClient, test_sales_transaction):
        """Test approving an already approved return"""
        transaction, items = test_sales_transaction
        
        # Create and approve a return
        create_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Already approved",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 1,
                    "condition": "GOOD"
                }
            ]
        }
        
        create_response = await async_client.post("/api/v1/sales/returns/", json=create_data)
        return_id = create_response.json()["id"]
        
        # First approval
        current_user_id = str(uuid4())
        await async_client.post(
            f"/api/v1/sales/returns/{return_id}/approve?current_user_id={current_user_id}",
            json={}
        )
        
        # Try to approve again
        response = await async_client.post(
            f"/api/v1/sales/returns/{return_id}/approve?current_user_id={current_user_id}",
            json={}
        )
        
        assert response.status_code == 400
        assert "already approved" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_return_summary(self, async_client: AsyncClient, test_sales_transaction):
        """Test getting return summary statistics"""
        transaction, items = test_sales_transaction
        
        # Create some returns
        for i in range(2):
            create_data = {
                "sales_transaction_id": str(transaction.id),
                "reason": f"Summary test {i}",
                "items": [
                    {
                        "sales_item_id": str(items[0].id),
                        "quantity": 1,
                        "condition": "GOOD"
                    }
                ],
                "restocking_fee": 10.0
            }
            response = await async_client.post("/api/v1/sales/returns/", json=create_data)
            
            # Approve first one
            if i == 0:
                return_id = response.json()["id"]
                await async_client.post(
                    f"/api/v1/sales/returns/{return_id}/approve?current_user_id={uuid4()}",
                    json={}
                )
        
        # Get summary
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        response = await async_client.get(
            f"/api/v1/sales/returns/summary/stats?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_returns"] >= 2
        assert data["approved_count"] >= 1
        assert data["pending_count"] >= 1
        assert float(data["total_refund_amount"]) > 0
    
    @pytest.mark.asyncio
    async def test_get_pending_approval_returns(self, async_client: AsyncClient, test_sales_transaction):
        """Test getting returns pending approval"""
        transaction, items = test_sales_transaction
        
        # Create pending return
        create_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Pending approval",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 1,
                    "condition": "DEFECTIVE"
                }
            ]
        }
        
        await async_client.post("/api/v1/sales/returns/", json=create_data)
        
        # Get pending returns
        response = await async_client.get("/api/v1/sales/returns/pending-approval")
        
        assert response.status_code == 200
        data = response.json()
        
        # All should be pending
        assert all(not r["is_approved"] for r in data)
        assert all(r["approved_by_id"] is None for r in data)
    
    @pytest.mark.asyncio
    async def test_get_returns_by_transaction(self, async_client: AsyncClient, test_sales_transaction):
        """Test getting all returns for a specific transaction"""
        transaction, items = test_sales_transaction
        
        # Create multiple returns for the transaction
        for i in range(2):
            create_data = {
                "sales_transaction_id": str(transaction.id),
                "reason": f"Return {i} for transaction",
                "items": [
                    {
                        "sales_item_id": str(items[0].id),
                        "quantity": 1,
                        "condition": "GOOD"
                    }
                ]
            }
            await async_client.post("/api/v1/sales/returns/", json=create_data)
        
        # Get returns by transaction
        response = await async_client.get(
            f"/api/v1/sales/returns/by-transaction/{transaction.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) >= 2
        assert all(r["sales_transaction_id"] == str(transaction.id) for r in data)
    
    @pytest.mark.asyncio
    async def test_create_return_excessive_quantity(self, async_client: AsyncClient, test_sales_transaction):
        """Test creating return with quantity exceeding original"""
        transaction, items = test_sales_transaction
        
        request_data = {
            "sales_transaction_id": str(transaction.id),
            "reason": "Trying to return too many",
            "items": [
                {
                    "sales_item_id": str(items[0].id),
                    "quantity": 5,  # Original was only 2
                    "condition": "GOOD"
                }
            ]
        }
        
        response = await async_client.post("/api/v1/sales/returns/", json=request_data)
        
        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"].lower()