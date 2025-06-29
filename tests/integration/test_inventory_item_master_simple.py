import pytest
from decimal import Decimal
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from unittest.mock import Mock, AsyncMock, patch

from src.api.v1.endpoints.inventory_item_masters import router as inventory_router
from src.domain.entities.inventory_item_master import InventoryItemMaster


@pytest.fixture
def app():
    """Create FastAPI app for testing"""
    app = FastAPI()
    app.include_router(inventory_router)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_inventory_service():
    """Mock inventory service"""
    service = Mock()
    service.create_inventory_item_master = AsyncMock()
    service.get_inventory_item_master = AsyncMock()
    service.get_inventory_item_master_by_sku = AsyncMock()
    service.update_inventory_item_master = AsyncMock()
    service.delete_inventory_item_master = AsyncMock()
    service.list_inventory_item_masters = AsyncMock()
    service.list_by_subcategory = AsyncMock()
    service.list_by_tracking_type = AsyncMock()
    service.list_consumables = AsyncMock()
    service.search_inventory_item_masters = AsyncMock()
    service.update_quantity = AsyncMock()
    service.update_dimensions = AsyncMock()
    service.count_inventory_item_masters = AsyncMock()
    return service


@pytest.fixture
def sample_inventory_item():
    """Sample inventory item for testing"""
    return InventoryItemMaster(
        inventory_id=uuid4(),
        name="MacBook Pro 16-inch",
        sku="MBP16-001",
        description="Apple MacBook Pro with M2 chip",
        item_sub_category_id=uuid4(),
        unit_of_measurement_id=uuid4(),
        tracking_type="INDIVIDUAL",
        brand="Apple",
        weight=Decimal("2.15"),
        renting_period=7,
        quantity=5
    )


@pytest.fixture
def sample_item_data():
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


class TestInventoryItemMasterAPIIntegration:
    """Integration tests for inventory item master API endpoints"""
    
    def test_create_inventory_item_success(self, client, mock_inventory_service, sample_item_data, sample_inventory_item):
        """Test successful inventory item creation"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.create_inventory_item_master.return_value = sample_inventory_item
            
            response = client.post("/inventory-items/", json=sample_item_data)
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            
            assert data["name"] == sample_item_data["name"]
            assert data["sku"] == sample_item_data["sku"]
            assert data["tracking_type"] == sample_item_data["tracking_type"]
            assert data["brand"] == sample_item_data["brand"]
    
    def test_create_inventory_item_validation_error(self, client, mock_inventory_service):
        """Test creation with validation error"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.create_inventory_item_master.side_effect = ValueError("Item name is required")
            
            invalid_data = {
                "name": "",
                "sku": "TEST-001",
                "item_sub_category_id": str(uuid4()),
                "unit_of_measurement_id": str(uuid4()),
                "tracking_type": "BULK"
            }
            
            response = client.post("/inventory-items/", json=invalid_data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_inventory_item_by_id_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test getting item by ID"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.get_inventory_item_master.return_value = sample_inventory_item
            
            response = client.get(f"/inventory-items/{sample_inventory_item.id}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["id"] == str(sample_inventory_item.id)
            assert data["name"] == sample_inventory_item.name
            assert data["sku"] == sample_inventory_item.sku
    
    def test_get_inventory_item_by_id_not_found(self, client, mock_inventory_service):
        """Test getting non-existent item by ID"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.get_inventory_item_master.return_value = None
            
            non_existent_id = str(uuid4())
            response = client.get(f"/inventory-items/{non_existent_id}")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_inventory_item_by_sku_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test getting item by SKU"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.get_inventory_item_master_by_sku.return_value = sample_inventory_item
            
            response = client.get(f"/inventory-items/by-sku/{sample_inventory_item.sku}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["sku"] == sample_inventory_item.sku
            assert data["name"] == sample_inventory_item.name
    
    def test_get_inventory_item_by_sku_not_found(self, client, mock_inventory_service):
        """Test getting non-existent item by SKU"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.get_inventory_item_master_by_sku.return_value = None
            
            response = client.get("/inventory-items/by-sku/NONEXISTENT-001")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_inventory_item_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test successful item update"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            updated_item = sample_inventory_item
            updated_item._name = "Updated MacBook Pro"
            mock_inventory_service.update_inventory_item_master.return_value = updated_item
            
            update_data = {
                "name": "Updated MacBook Pro",
                "description": "Updated description"
            }
            
            response = client.put(f"/inventory-items/{sample_inventory_item.id}", json=update_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["name"] == "Updated MacBook Pro"
    
    def test_update_inventory_item_not_found(self, client, mock_inventory_service):
        """Test updating non-existent item"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.update_inventory_item_master.side_effect = ValueError("not found")
            
            non_existent_id = str(uuid4())
            update_data = {"name": "Updated Name"}
            
            response = client.put(f"/inventory-items/{non_existent_id}", json=update_data)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_inventory_item_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test successful item deletion"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.delete_inventory_item_master.return_value = True
            
            response = client.delete(f"/inventory-items/{sample_inventory_item.id}")
            
            assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_inventory_item_not_found(self, client, mock_inventory_service):
        """Test deleting non-existent item"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.delete_inventory_item_master.return_value = False
            
            non_existent_id = str(uuid4())
            response = client.delete(f"/inventory-items/{non_existent_id}")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_inventory_items_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test listing items with pagination"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.list_inventory_item_masters.return_value = [sample_inventory_item]
            mock_inventory_service.count_inventory_item_masters.return_value = 1
            
            response = client.get("/inventory-items/?skip=0&limit=10")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert "items" in data
            assert "total" in data
            assert "skip" in data
            assert "limit" in data
            assert len(data["items"]) == 1
            assert data["total"] == 1
            assert data["skip"] == 0
            assert data["limit"] == 10
    
    def test_list_by_tracking_type_individual(self, client, mock_inventory_service, sample_inventory_item):
        """Test listing items by tracking type - INDIVIDUAL"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.list_by_tracking_type.return_value = [sample_inventory_item]
            
            response = client.get("/inventory-items/by-tracking-type/INDIVIDUAL")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 1
            assert data[0]["tracking_type"] == "INDIVIDUAL"
    
    def test_list_by_invalid_tracking_type(self, client, mock_inventory_service):
        """Test listing items by invalid tracking type"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            response = client.get("/inventory-items/by-tracking-type/INVALID")
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_search_inventory_items(self, client, mock_inventory_service, sample_inventory_item):
        """Test searching items"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.search_inventory_item_masters.return_value = [sample_inventory_item]
            
            response = client.get("/inventory-items/search/?query=MacBook")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert isinstance(data, list)
            assert len(data) == 1
            assert "MacBook" in data[0]["name"]
    
    def test_search_items_empty_query(self, client, mock_inventory_service):
        """Test searching items with empty query"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            response = client.get("/inventory-items/search/?query=")
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_quantity_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test successful quantity update"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.update_quantity.return_value = True
            
            quantity_data = {"quantity": 50}
            response = client.patch(f"/inventory-items/{sample_inventory_item.id}/quantity", json=quantity_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert data["message"] == "Quantity updated successfully"
            assert data["new_quantity"] == 50
    
    def test_update_quantity_not_found(self, client, mock_inventory_service):
        """Test quantity update for non-existent item"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.update_quantity.return_value = False
            
            non_existent_id = str(uuid4())
            quantity_data = {"quantity": 50}
            
            response = client.patch(f"/inventory-items/{non_existent_id}/quantity", json=quantity_data)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_dimensions_success(self, client, mock_inventory_service, sample_inventory_item):
        """Test successful dimensions update"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            updated_item = sample_inventory_item
            updated_item._weight = Decimal("2.5")
            mock_inventory_service.update_dimensions.return_value = updated_item
            
            dimensions_data = {
                "weight": "2.5",
                "length": "40.0"
            }
            
            response = client.patch(f"/inventory-items/{sample_inventory_item.id}/dimensions", json=dimensions_data)
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            
            assert float(data["weight"]) == 2.5
    
    def test_update_dimensions_not_found(self, client, mock_inventory_service):
        """Test dimensions update for non-existent item"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            mock_inventory_service.update_dimensions.side_effect = ValueError("not found")
            
            non_existent_id = str(uuid4())
            dimensions_data = {"weight": "2.0"}
            
            response = client.patch(f"/inventory-items/{non_existent_id}/dimensions", json=dimensions_data)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_api_pagination_edge_cases(self, client, mock_inventory_service):
        """Test API pagination edge cases"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            # Test negative skip
            response = client.get("/inventory-items/?skip=-1&limit=10")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test zero limit
            response = client.get("/inventory-items/?skip=0&limit=0")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test excessive limit
            response = client.get("/inventory-items/?skip=0&limit=2000")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_api_error_handling(self, client, mock_inventory_service):
        """Test API error handling"""
        with patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service', return_value=mock_inventory_service):
            # Invalid UUID format
            response = client.get("/inventory-items/invalid-uuid")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY