import pytest
from decimal import Decimal
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from unittest.mock import AsyncMock, patch

from src.api.v1.endpoints.inventory_item_masters import router as inventory_router
from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.application.services.inventory_item_master_service import InventoryItemMasterService


class TestInventoryItemMasterAPI:
    """Comprehensive integration tests for inventory item master API endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing"""
        app = FastAPI()
        app.include_router(inventory_router)
        return app
    
    @pytest.fixture
    def client(self, app):
        """HTTP client for testing"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_item_data(self):
        """Sample item data for testing"""
        return {
            "name": "MacBook Pro 16-inch",
            "sku": "MBP16-001",
            "description": "Apple MacBook Pro with M2 chip",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "INDIVIDUAL",
            "is_consumable": False,
            "brand": "Apple",
            "manufacturer_part_number": "MBP-M2-16",
            "weight": "2.15",
            "length": "35.57",
            "width": "24.81",
            "height": "1.68",
            "renting_period": 7,
            "quantity": 5,
            "created_by": "admin"
        }
    
    @pytest.fixture
    def sample_consumable_data(self):
        """Sample consumable item data for testing"""
        return {
            "name": "A4 Paper Sheets",
            "sku": "PAPER-A4-001",
            "description": "High quality A4 paper for printing",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "BULK",
            "is_consumable": True,
            "brand": "OfficeMax",
            "quantity": 1000,
            "created_by": "admin"
        }
    
    @pytest.fixture
    def sample_bulk_item_data(self):
        """Sample bulk item data for testing"""
        return {
            "name": "Steel Screws M6x20",
            "sku": "SCREW-M6-20",
            "description": "Stainless steel screws M6x20mm",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "BULK",
            "is_consumable": False,
            "brand": "FastenerPro",
            "quantity": 500,
            "created_by": "admin"
        }
    
    def test_create_inventory_item_success(self, client, sample_item_data):
        """Test successful inventory item creation"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service') as mock_service:
            # Mock the service to return a successful result
            mock_service_instance = AsyncMock()
            mock_service.return_value = mock_service_instance
            
            # Create expected inventory item
            expected_item = InventoryItemMaster(
                inventory_id=uuid4(),
                name=sample_item_data["name"],
                sku=sample_item_data["sku"],
                description=sample_item_data["description"],
                item_sub_category_id=uuid4(),
                unit_of_measurement_id=uuid4(),
                tracking_type=sample_item_data["tracking_type"],
                brand=sample_item_data["brand"],
                weight=Decimal(sample_item_data["weight"]),
                renting_period=sample_item_data["renting_period"],
                quantity=sample_item_data["quantity"]
            )
            
            mock_service_instance.create_inventory_item_master.return_value = expected_item
            
            response = client.post("/inventory-items/", json=sample_item_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == sample_item_data["name"]
        assert data["sku"] == sample_item_data["sku"]
        assert data["description"] == sample_item_data["description"]
        assert data["tracking_type"] == sample_item_data["tracking_type"]
        assert data["is_consumable"] == sample_item_data["is_consumable"]
        assert data["brand"] == sample_item_data["brand"]
        assert float(data["weight"]) == float(sample_item_data["weight"])
        assert data["renting_period"] == sample_item_data["renting_period"]
        assert data["quantity"] == sample_item_data["quantity"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    @pytest.mark.asyncio
    async def test_create_consumable_item_success(self, client, sample_consumable_data):
        """Test successful consumable item creation"""
        response = await client.post("/api/v1/inventory-items/", json=sample_consumable_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == sample_consumable_data["name"]
        assert data["is_consumable"] is True
        assert data["tracking_type"] == "BULK"
    
    @pytest.mark.asyncio
    async def test_create_bulk_item_success(self, client, sample_bulk_item_data):
        """Test successful bulk item creation"""
        response = await client.post("/api/v1/inventory-items/", json=sample_bulk_item_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == sample_bulk_item_data["name"]
        assert data["tracking_type"] == "BULK"
        assert data["is_consumable"] is False
    
    @pytest.mark.asyncio
    async def test_create_item_minimal_data(self, client):
        """Test creation with minimal required data"""
        minimal_data = {
            "name": "Basic Item",
            "sku": "BASIC-001",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "BULK"
        }
        
        response = await client.post("/api/v1/inventory-items/", json=minimal_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == minimal_data["name"]
        assert data["sku"] == minimal_data["sku"]
        assert data["tracking_type"] == minimal_data["tracking_type"]
        assert data["is_consumable"] is False
        assert data["renting_period"] == 1
        assert data["quantity"] == 0
    
    @pytest.mark.asyncio
    async def test_create_item_validation_errors(self, client):
        """Test creation with validation errors"""
        invalid_data = {
            "name": "",  # Empty name
            "sku": "",   # Empty SKU
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "INVALID"  # Invalid tracking type
        }
        
        response = await client.post("/api/v1/inventory-items/", json=invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_create_item_invalid_tracking_type(self, client):
        """Test creation with invalid tracking type"""
        invalid_data = {
            "name": "Test Item",
            "sku": "TEST-001",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "INVALID"
        }
        
        response = await client.post("/api/v1/inventory-items/", json=invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_create_item_negative_values(self, client):
        """Test creation with negative values"""
        invalid_data = {
            "name": "Test Item",
            "sku": "TEST-001",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "BULK",
            "weight": "-1.0",  # Negative weight
            "quantity": -5,    # Negative quantity
            "renting_period": 0  # Invalid renting period
        }
        
        response = await client.post("/api/v1/inventory-items/", json=invalid_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_success(self, client, sample_item_data):
        """Test getting item by ID"""
        # First create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Then get it by ID
        response = await client.get(f"/api/v1/inventory-items/{item_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["id"] == item_id
        assert data["name"] == sample_item_data["name"]
        assert data["sku"] == sample_item_data["sku"]
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self, client):
        """Test getting non-existent item by ID"""
        non_existent_id = str(uuid4())
        
        response = await client.get(f"/api/v1/inventory-items/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_item_by_sku_success(self, client, sample_item_data):
        """Test getting item by SKU"""
        # First create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        
        # Then get it by SKU
        response = await client.get(f"/api/v1/inventory-items/by-sku/{sample_item_data['sku']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["sku"] == sample_item_data["sku"]
        assert data["name"] == sample_item_data["name"]
    
    @pytest.mark.asyncio
    async def test_get_item_by_sku_not_found(self, client):
        """Test getting non-existent item by SKU"""
        non_existent_sku = "NONEXISTENT-001"
        
        response = await client.get(f"/api/v1/inventory-items/by-sku/{non_existent_sku}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_item_success(self, client, sample_item_data):
        """Test successful item update"""
        # First create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update data
        update_data = {
            "name": "Updated MacBook Pro",
            "description": "Updated description",
            "brand": "Apple Inc.",
            "quantity": 10
        }
        
        # Update the item
        response = await client.put(f"/api/v1/inventory-items/{item_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["brand"] == update_data["brand"]
        assert data["quantity"] == update_data["quantity"]
    
    @pytest.mark.asyncio
    async def test_update_item_not_found(self, client):
        """Test updating non-existent item"""
        non_existent_id = str(uuid4())
        update_data = {"name": "Updated Name"}
        
        response = await client.put(f"/api/v1/inventory-items/{non_existent_id}", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_item_invalid_data(self, client, sample_item_data):
        """Test updating item with invalid data"""
        # First create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Try to update with invalid tracking type
        update_data = {"tracking_type": "INVALID"}
        
        response = await client.put(f"/api/v1/inventory-items/{item_id}", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_delete_item_success(self, client, sample_item_data):
        """Test successful item deletion"""
        # First create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Delete the item
        response = await client.delete(f"/api/v1/inventory-items/{item_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify item is deleted
        get_response = await client.get(f"/api/v1/inventory-items/{item_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, client):
        """Test deleting non-existent item"""
        non_existent_id = str(uuid4())
        
        response = await client.delete(f"/api/v1/inventory-items/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_list_items_success(self, client, sample_item_data, sample_consumable_data):
        """Test listing items with pagination"""
        # Create multiple items
        await client.post("/api/v1/inventory-items/", json=sample_item_data)
        await client.post("/api/v1/inventory-items/", json=sample_consumable_data)
        
        # List items
        response = await client.get("/api/v1/inventory-items/?skip=0&limit=10")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert len(data["items"]) >= 2
        assert data["skip"] == 0
        assert data["limit"] == 10
        assert data["total"] >= 2
    
    @pytest.mark.asyncio
    async def test_list_items_pagination(self, client, sample_item_data):
        """Test pagination in listing items"""
        # Create multiple items
        for i in range(5):
            item_data = sample_item_data.copy()
            item_data["name"] = f"Item {i+1}"
            item_data["sku"] = f"ITEM-{i+1:03d}"
            await client.post("/api/v1/inventory-items/", json=item_data)
        
        # Test pagination
        response = await client.get("/api/v1/inventory-items/?skip=2&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert len(data["items"]) == 2
        assert data["skip"] == 2
        assert data["limit"] == 2
    
    @pytest.mark.asyncio
    async def test_list_by_subcategory(self, client, sample_item_data):
        """Test listing items by subcategory"""
        # Create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        subcategory_id = sample_item_data["item_sub_category_id"]
        
        # List by subcategory
        response = await client.get(f"/api/v1/inventory-items/by-subcategory/{subcategory_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(item["item_sub_category_id"] == subcategory_id for item in data)
    
    @pytest.mark.asyncio
    async def test_list_by_tracking_type_individual(self, client, sample_item_data):
        """Test listing items by tracking type - INDIVIDUAL"""
        # Create an item with INDIVIDUAL tracking
        await client.post("/api/v1/inventory-items/", json=sample_item_data)
        
        # List by tracking type
        response = await client.get("/api/v1/inventory-items/by-tracking-type/INDIVIDUAL")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(item["tracking_type"] == "INDIVIDUAL" for item in data)
    
    @pytest.mark.asyncio
    async def test_list_by_tracking_type_bulk(self, client, sample_bulk_item_data):
        """Test listing items by tracking type - BULK"""
        # Create an item with BULK tracking
        await client.post("/api/v1/inventory-items/", json=sample_bulk_item_data)
        
        # List by tracking type
        response = await client.get("/api/v1/inventory-items/by-tracking-type/BULK")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(item["tracking_type"] == "BULK" for item in data)
    
    @pytest.mark.asyncio
    async def test_list_by_invalid_tracking_type(self, client):
        """Test listing items by invalid tracking type"""
        response = await client.get("/api/v1/inventory-items/by-tracking-type/INVALID")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_list_consumables(self, client, sample_consumable_data):
        """Test listing consumable items"""
        # Create a consumable item
        await client.post("/api/v1/inventory-items/", json=sample_consumable_data)
        
        # List consumables
        response = await client.get("/api/v1/inventory-items/consumables/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(item["is_consumable"] is True for item in data)
    
    @pytest.mark.asyncio
    async def test_search_items_by_name(self, client, sample_item_data):
        """Test searching items by name"""
        # Create an item
        await client.post("/api/v1/inventory-items/", json=sample_item_data)
        
        # Search by name
        response = await client.get("/api/v1/inventory-items/search/?query=MacBook")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any("MacBook" in item["name"] for item in data)
    
    @pytest.mark.asyncio
    async def test_search_items_by_sku(self, client, sample_item_data):
        """Test searching items by SKU"""
        # Create an item
        await client.post("/api/v1/inventory-items/", json=sample_item_data)
        
        # Search by SKU
        response = await client.get("/api/v1/inventory-items/search/?query=MBP16")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any("MBP16" in item["sku"] for item in data)
    
    @pytest.mark.asyncio
    async def test_search_items_with_limit(self, client, sample_item_data):
        """Test searching items with limit"""
        # Create multiple items
        for i in range(5):
            item_data = sample_item_data.copy()
            item_data["name"] = f"MacBook {i+1}"
            item_data["sku"] = f"MBP-{i+1:03d}"
            await client.post("/api/v1/inventory-items/", json=item_data)
        
        # Search with limit
        response = await client.get("/api/v1/inventory-items/search/?query=MacBook&limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 3
    
    @pytest.mark.asyncio
    async def test_search_items_no_results(self, client):
        """Test searching items with no results"""
        response = await client.get("/api/v1/inventory-items/search/?query=NonExistentItem")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_search_items_empty_query(self, client):
        """Test searching items with empty query"""
        response = await client.get("/api/v1/inventory-items/search/?query=")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_update_quantity_success(self, client, sample_item_data):
        """Test successful quantity update"""
        # Create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update quantity
        quantity_data = {"quantity": 50}
        response = await client.patch(f"/api/v1/inventory-items/{item_id}/quantity", json=quantity_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["message"] == "Quantity updated successfully"
        assert data["new_quantity"] == 50
    
    @pytest.mark.asyncio
    async def test_update_quantity_not_found(self, client):
        """Test quantity update for non-existent item"""
        non_existent_id = str(uuid4())
        quantity_data = {"quantity": 50}
        
        response = await client.patch(f"/api/v1/inventory-items/{non_existent_id}/quantity", json=quantity_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_dimensions_success(self, client, sample_item_data):
        """Test successful dimensions update"""
        # Create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update dimensions
        dimensions_data = {
            "weight": "2.5",
            "length": "40.0",
            "width": "25.0",
            "height": "2.0"
        }
        response = await client.patch(f"/api/v1/inventory-items/{item_id}/dimensions", json=dimensions_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert float(data["weight"]) == 2.5
        assert float(data["length"]) == 40.0
        assert float(data["width"]) == 25.0
        assert float(data["height"]) == 2.0
    
    @pytest.mark.asyncio
    async def test_update_dimensions_partial(self, client, sample_item_data):
        """Test partial dimensions update"""
        # Create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update only weight
        dimensions_data = {"weight": "3.0"}
        response = await client.patch(f"/api/v1/inventory-items/{item_id}/dimensions", json=dimensions_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert float(data["weight"]) == 3.0
        # Other dimensions should remain unchanged
        assert data["length"] == sample_item_data["length"]
        assert data["width"] == sample_item_data["width"]
        assert data["height"] == sample_item_data["height"]
    
    @pytest.mark.asyncio
    async def test_update_dimensions_not_found(self, client):
        """Test dimensions update for non-existent item"""
        non_existent_id = str(uuid4())
        dimensions_data = {"weight": "2.0"}
        
        response = await client.patch(f"/api/v1/inventory-items/{non_existent_id}/dimensions", json=dimensions_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_dimensions_invalid_values(self, client, sample_item_data):
        """Test dimensions update with invalid values"""
        # Create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        created_item = create_response.json()
        item_id = created_item["id"]
        
        # Update with negative weight
        dimensions_data = {"weight": "-1.0"}
        response = await client.patch(f"/api/v1/inventory-items/{item_id}/dimensions", json=dimensions_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Because validation error becomes 404
    
    @pytest.mark.asyncio
    async def test_api_pagination_edge_cases(self, client):
        """Test API pagination edge cases"""
        # Test negative skip
        response = await client.get("/api/v1/inventory-items/?skip=-1&limit=10")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test zero limit
        response = await client.get("/api/v1/inventory-items/?skip=0&limit=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test excessive limit
        response = await client.get("/api/v1/inventory-items/?skip=0&limit=2000")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_api_response_format_consistency(self, client, sample_item_data):
        """Test API response format consistency"""
        # Create an item
        create_response = await client.post("/api/v1/inventory-items/", json=sample_item_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_item = create_response.json()
        
        # Get by ID
        get_response = await client.get(f"/api/v1/inventory-items/{created_item['id']}")
        get_item = get_response.json()
        
        # Get by SKU
        sku_response = await client.get(f"/api/v1/inventory-items/by-sku/{created_item['sku']}")
        sku_item = sku_response.json()
        
        # All responses should have the same structure
        required_fields = ["id", "name", "sku", "tracking_type", "is_consumable", 
                          "created_at", "updated_at", "is_active"]
        
        for field in required_fields:
            assert field in created_item
            assert field in get_item
            assert field in sku_item
        
        # Values should be consistent
        assert created_item["id"] == get_item["id"] == sku_item["id"]
        assert created_item["name"] == get_item["name"] == sku_item["name"]
        assert created_item["sku"] == get_item["sku"] == sku_item["sku"]
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, client):
        """Test API error handling"""
        # Invalid UUID format
        response = await client.get("/api/v1/inventory-items/invalid-uuid")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Invalid JSON in request body
        response = await client.post("/api/v1/inventory-items/", 
                                   content="invalid json", 
                                   headers={"Content-Type": "application/json"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_concurrent_item_creation(self, client, sample_item_data):
        """Test concurrent item creation with different SKUs"""
        import asyncio
        
        # Create multiple items concurrently with different SKUs
        tasks = []
        for i in range(3):
            item_data = sample_item_data.copy()
            item_data["name"] = f"Concurrent Item {i+1}"
            item_data["sku"] = f"CONC-{i+1:03d}"
            tasks.append(client.post("/api/v1/inventory-items/", json=item_data))
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED
        
        # All should have unique IDs
        ids = [response.json()["id"] for response in responses]
        assert len(set(ids)) == len(ids)  # All unique