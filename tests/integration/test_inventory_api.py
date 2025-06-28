import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from decimal import Decimal
from fastapi.testclient import TestClient
from fastapi import FastAPI

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
    service.search_inventory_item_masters = AsyncMock()
    service.count_inventory_item_masters = AsyncMock()
    service.update_quantity = AsyncMock()
    service.update_dimensions = AsyncMock()
    return service


@pytest.mark.integration
class TestInventoryItemMasterAPI:
    """Integration tests for InventoryItemMaster API endpoints"""

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_create_inventory_item_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item_data):
        """Test successful inventory item creation"""
        mock_get_service.return_value = mock_inventory_service
        
        inventory_item = InventoryItemMaster(
            name=sample_inventory_item_data["name"],
            sku=sample_inventory_item_data["sku"],
            item_sub_category_id=uuid4(),
            unit_of_measurement_id=uuid4(),
            tracking_type=sample_inventory_item_data["tracking_type"],
            brand=sample_inventory_item_data["brand"],
            weight=sample_inventory_item_data["weight"],
            quantity=sample_inventory_item_data["quantity"]
        )
        
        mock_inventory_service.create_inventory_item_master.return_value = inventory_item
        
        request_data = {
            "name": sample_inventory_item_data["name"],
            "sku": sample_inventory_item_data["sku"],
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": sample_inventory_item_data["tracking_type"],
            "brand": sample_inventory_item_data["brand"],
            "weight": float(sample_inventory_item_data["weight"]),
            "quantity": sample_inventory_item_data["quantity"]
        }
        
        response = client.post("/inventory-items/", json=request_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_inventory_item_data["name"]
        assert data["sku"] == sample_inventory_item_data["sku"].upper()
        assert data["tracking_type"] == sample_inventory_item_data["tracking_type"]

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_create_inventory_item_validation_error(self, mock_get_service, client, mock_inventory_service):
        """Test inventory item creation with validation error"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.create_inventory_item_master.side_effect = ValueError("SKU already exists")
        
        request_data = {
            "name": "Test Item",
            "sku": "EXISTING-SKU",
            "item_sub_category_id": str(uuid4()),
            "unit_of_measurement_id": str(uuid4()),
            "tracking_type": "INDIVIDUAL"
        }
        
        response = client.post("/inventory-items/", json=request_data)
        
        assert response.status_code == 400
        assert "SKU already exists" in response.json()["detail"]

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_get_inventory_item_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful inventory item retrieval"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.get_inventory_item_master.return_value = sample_inventory_item
        
        item_id = uuid4()
        response = client.get(f"/inventory-items/{item_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_inventory_item.name
        assert data["sku"] == sample_inventory_item.sku

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_get_inventory_item_not_found(self, mock_get_service, client, mock_inventory_service):
        """Test inventory item retrieval when not found"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.get_inventory_item_master.return_value = None
        
        item_id = uuid4()
        response = client.get(f"/inventory-items/{item_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_get_inventory_item_by_sku_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful inventory item retrieval by SKU"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.get_inventory_item_master_by_sku.return_value = sample_inventory_item
        
        sku = "TEST-SKU-001"
        response = client.get(f"/inventory-items/by-sku/{sku}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_inventory_item.name

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_update_inventory_item_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful inventory item update"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.update_inventory_item_master.return_value = sample_inventory_item
        
        item_id = uuid4()
        update_data = {
            "name": "Updated Item Name",
            "brand": "Updated Brand"
        }
        
        response = client.put(f"/inventory-items/{item_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_inventory_item.name

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_delete_inventory_item_success(self, mock_get_service, client, mock_inventory_service):
        """Test successful inventory item deletion"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.delete_inventory_item_master.return_value = True
        
        item_id = uuid4()
        response = client.delete(f"/inventory-items/{item_id}")
        
        assert response.status_code == 204

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_delete_inventory_item_not_found(self, mock_get_service, client, mock_inventory_service):
        """Test inventory item deletion when not found"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.delete_inventory_item_master.return_value = False
        
        item_id = uuid4()
        response = client.delete(f"/inventory-items/{item_id}")
        
        assert response.status_code == 404

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_list_inventory_items_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful inventory items listing"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.list_inventory_item_masters.return_value = [sample_inventory_item]
        mock_inventory_service.count_inventory_item_masters.return_value = 1
        
        response = client.get("/inventory-items/?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == sample_inventory_item.name

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_search_inventory_items_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful inventory items search"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.search_inventory_item_masters.return_value = [sample_inventory_item]
        
        response = client.get("/inventory-items/search/?query=laptop&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_inventory_item.name

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_update_quantity_success(self, mock_get_service, client, mock_inventory_service):
        """Test successful quantity update"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.update_quantity.return_value = True
        
        item_id = uuid4()
        update_data = {"quantity": 25}
        
        response = client.patch(f"/inventory-items/{item_id}/quantity", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "successfully" in data["message"]
        assert data["new_quantity"] == 25

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_update_quantity_not_found(self, mock_get_service, client, mock_inventory_service):
        """Test quantity update when item not found"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.update_quantity.return_value = False
        
        item_id = uuid4()
        update_data = {"quantity": 25}
        
        response = client.patch(f"/inventory-items/{item_id}/quantity", json=update_data)
        
        assert response.status_code == 404

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_update_dimensions_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful dimensions update"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.update_dimensions.return_value = sample_inventory_item
        
        item_id = uuid4()
        update_data = {
            "weight": 3.5,
            "length": 40.0,
            "width": 30.0,
            "height": 2.0
        }
        
        response = client.patch(f"/inventory-items/{item_id}/dimensions", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_inventory_item.name

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_list_by_tracking_type_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful listing by tracking type"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.list_by_tracking_type.return_value = [sample_inventory_item]
        
        response = client.get("/inventory-items/by-tracking-type/INDIVIDUAL?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_inventory_item.name

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_list_by_tracking_type_invalid(self, mock_get_service, client, mock_inventory_service):
        """Test listing by invalid tracking type"""
        mock_get_service.return_value = mock_inventory_service
        
        response = client.get("/inventory-items/by-tracking-type/INVALID")
        
        assert response.status_code == 400
        assert "Invalid tracking type" in response.json()["detail"]

    @patch('src.api.v1.endpoints.inventory_item_masters.get_inventory_item_master_service')
    def test_list_consumables_success(self, mock_get_service, client, mock_inventory_service, sample_inventory_item):
        """Test successful consumables listing"""
        mock_get_service.return_value = mock_inventory_service
        mock_inventory_service.list_consumables.return_value = [sample_inventory_item]
        
        response = client.get("/inventory-items/consumables/?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == sample_inventory_item.name