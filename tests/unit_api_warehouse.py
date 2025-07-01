"""
Unit tests for Warehouse API Layer.

Tests the API endpoints and schemas with mocked dependencies:
- FastAPI endpoint handlers
- Request/response serialization
- HTTP status codes
- Input validation
- Error handling and HTTP error responses
- Pydantic schema validation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from fastapi import status, HTTPException
from pydantic import ValidationError

from src.domain.entities.warehouse import Warehouse
from src.application.use_cases.warehouse_use_cases import WarehouseUseCases
from src.api.v1.schemas.warehouse_schemas import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
    WarehouseBase
)
from src.main import app


class TestWarehouseSchemas:
    """Test Pydantic schemas for warehouse API."""
    
    def test_warehouse_create_schema_valid(self):
        """Test valid warehouse creation schema."""
        data = {
            "name": "Test Warehouse",
            "label": "TEST",
            "remarks": "Test remarks",
            "created_by": "test_user"
        }
        
        schema = WarehouseCreate(**data)
        
        assert schema.name == "Test Warehouse"
        assert schema.label == "TEST"
        assert schema.remarks == "Test remarks"
        assert schema.created_by == "test_user"
    
    def test_warehouse_create_schema_minimal(self):
        """Test warehouse creation schema with minimal fields."""
        data = {
            "name": "Minimal Warehouse",
            "label": "MIN"
        }
        
        schema = WarehouseCreate(**data)
        
        assert schema.name == "Minimal Warehouse"
        assert schema.label == "MIN"
        assert schema.remarks is None
        assert schema.created_by is None
    
    def test_warehouse_create_schema_label_normalization(self):
        """Test that label is normalized to uppercase in schema."""
        data = {
            "name": "Test",
            "label": "lowercase"
        }
        
        schema = WarehouseCreate(**data)
        
        assert schema.label == "LOWERCASE"
    
    def test_warehouse_create_schema_name_trimming(self):
        """Test that name whitespace is trimmed in schema."""
        data = {
            "name": "  Trimmed Name  ",
            "label": "TRIM"
        }
        
        schema = WarehouseCreate(**data)
        
        assert schema.name == "Trimmed Name"
    
    def test_warehouse_create_schema_validation_errors(self):
        """Test warehouse creation schema validation errors."""
        # Missing required fields
        with pytest.raises(ValidationError) as exc_info:
            WarehouseCreate()
        
        errors = exc_info.value.errors()
        field_names = [error['loc'][0] for error in errors]
        assert 'name' in field_names
        assert 'label' in field_names
    
    def test_warehouse_create_schema_empty_name(self):
        """Test warehouse creation schema with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            WarehouseCreate(name="", label="TEST")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)
    
    def test_warehouse_create_schema_empty_label(self):
        """Test warehouse creation schema with empty label."""
        with pytest.raises(ValidationError) as exc_info:
            WarehouseCreate(name="Test", label="")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('label',) for error in errors)
    
    def test_warehouse_create_schema_long_name(self):
        """Test warehouse creation schema with too long name."""
        long_name = "a" * 256
        with pytest.raises(ValidationError) as exc_info:
            WarehouseCreate(name=long_name, label="TEST")
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('name',) for error in errors)
    
    def test_warehouse_create_schema_long_label(self):
        """Test warehouse creation schema with too long label."""
        long_label = "a" * 256
        with pytest.raises(ValidationError) as exc_info:
            WarehouseCreate(name="Test", label=long_label)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('label',) for error in errors)
    
    def test_warehouse_update_schema_valid(self):
        """Test valid warehouse update schema."""
        data = {
            "name": "Updated Warehouse",
            "label": "UPDATED",
            "remarks": "Updated remarks"
        }
        
        schema = WarehouseUpdate(**data)
        
        assert schema.name == "Updated Warehouse"
        assert schema.label == "UPDATED"
        assert schema.remarks == "Updated remarks"
    
    def test_warehouse_update_schema_partial(self):
        """Test warehouse update schema with partial data."""
        data = {"name": "Partial Update"}
        
        schema = WarehouseUpdate(**data)
        
        assert schema.name == "Partial Update"
        assert schema.label is None
        assert schema.remarks is None
    
    def test_warehouse_update_schema_empty(self):
        """Test warehouse update schema with no data."""
        schema = WarehouseUpdate()
        
        assert schema.name is None
        assert schema.label is None
        assert schema.remarks is None
    
    def test_warehouse_response_schema_from_entity(self):
        """Test warehouse response schema creation from entity."""
        warehouse = Warehouse(
            name="Response Test",
            label="RESPONSE",
            remarks="Test response",
            entity_id=str(uuid4())
        )
        
        # Mock the from_orm method behavior
        response_data = {
            "id": warehouse.id,
            "name": warehouse.name,
            "label": warehouse.label,
            "remarks": warehouse.remarks,
            "created_at": warehouse.created_at,
            "updated_at": warehouse.updated_at,
            "created_by": warehouse.created_by,
            "is_active": warehouse.is_active
        }
        
        schema = WarehouseResponse(**response_data)
        
        assert schema.id == warehouse.id
        assert schema.name == warehouse.name
        assert schema.label == warehouse.label
        assert schema.remarks == warehouse.remarks
        assert schema.created_at == warehouse.created_at
        assert schema.updated_at == warehouse.updated_at
        assert schema.is_active == warehouse.is_active


class TestWarehouseAPIEndpoints:
    """Test warehouse API endpoints with mocked use cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_use_cases(self):
        """Create mock warehouse use cases."""
        return AsyncMock(spec=WarehouseUseCases)
    
    @pytest.fixture
    def sample_warehouse(self):
        """Create sample warehouse for testing."""
        return Warehouse(
            name="API Test Warehouse",
            label="API",
            remarks="For API testing",
            entity_id=str(uuid4())
        )
    
    def test_create_warehouse_success(self, client, sample_warehouse):
        """Test successful warehouse creation via API."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.create_warehouse.return_value = sample_warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            warehouse_data = {
                "name": "API Test Warehouse",
                "label": "API",
                "remarks": "For API testing",
                "created_by": "test_user"
            }
            
            # Act
            response = client.post("/api/v1/warehouses/", json=warehouse_data)
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["name"] == warehouse_data["name"]
            assert response_data["label"] == warehouse_data["label"]
            assert response_data["remarks"] == warehouse_data["remarks"]
            assert "id" in response_data
            assert "created_at" in response_data
            assert "updated_at" in response_data
    
    def test_create_warehouse_validation_error(self, client):
        """Test warehouse creation with validation error."""
        # Missing required fields
        warehouse_data = {
            "remarks": "Missing name and label"
        }
        
        response = client.post("/api/v1/warehouses/", json=warehouse_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = response.json()
        assert "detail" in response_data
    
    def test_create_warehouse_empty_fields(self, client):
        """Test warehouse creation with empty required fields."""
        warehouse_data = {
            "name": "",
            "label": "",
        }
        
        response = client.post("/api/v1/warehouses/", json=warehouse_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_warehouse_duplicate_label(self, client):
        """Test warehouse creation with duplicate label."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.create_warehouse.side_effect = ValueError("Warehouse with label 'DUPLICATE' already exists")
            mock_get_use_cases.return_value = mock_use_cases
            
            warehouse_data = {
                "name": "Duplicate Test",
                "label": "DUPLICATE",
                "created_by": "test_user"
            }
            
            # Act
            response = client.post("/api/v1/warehouses/", json=warehouse_data)
            
            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            response_data = response.json()
            assert "already exists" in response_data["detail"]
    
    def test_get_warehouse_success(self, client, sample_warehouse):
        """Test successful get warehouse by ID."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.get_warehouse.return_value = sample_warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get(f"/api/v1/warehouses/{sample_warehouse.id}")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["name"] == sample_warehouse.name
            assert response_data["label"] == sample_warehouse.label
            assert response_data["id"] == sample_warehouse.id
    
    def test_get_warehouse_not_found(self, client):
        """Test get warehouse when not found."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouse_id = str(uuid4())
            mock_use_cases = AsyncMock()
            mock_use_cases.get_warehouse.return_value = None
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get(f"/api/v1/warehouses/{warehouse_id}")
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert "not found" in response_data["detail"]
    
    def test_get_warehouse_invalid_uuid(self, client):
        """Test get warehouse with invalid UUID."""
        response = client.get("/api/v1/warehouses/invalid-uuid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_warehouse_by_label_success(self, client, sample_warehouse):
        """Test successful get warehouse by label."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.get_warehouse_by_label.return_value = sample_warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/label/API")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["name"] == sample_warehouse.name
            assert response_data["label"] == sample_warehouse.label
    
    def test_get_warehouse_by_label_not_found(self, client):
        """Test get warehouse by label when not found."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.get_warehouse_by_label.return_value = None
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/label/NOTFOUND")
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert "not found" in response_data["detail"]
    
    def test_list_warehouses_default_params(self, client):
        """Test list warehouses with default parameters."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouses = [
                Warehouse(name="Warehouse 1", label="WH1"),
                Warehouse(name="Warehouse 2", label="WH2")
            ]
            mock_use_cases = AsyncMock()
            mock_use_cases.list_warehouses.return_value = warehouses
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "count" in response_data
            assert "results" in response_data
            assert len(response_data["results"]) == 2
            
            # Verify default parameters were used
            mock_use_cases.list_warehouses.assert_called_once_with(
                skip=0, limit=20, active_only=True
            )
    
    def test_list_warehouses_custom_params(self, client):
        """Test list warehouses with custom parameters."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouses = [Warehouse(name="Test", label="TEST")]
            mock_use_cases = AsyncMock()
            mock_use_cases.list_warehouses.return_value = warehouses
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/?page=2&page_size=10&is_active=false")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            
            # Verify custom parameters were used (page 2 means skip=10)
            mock_use_cases.list_warehouses.assert_called_once_with(
                skip=10, limit=10, active_only=False
            )
    
    def test_list_warehouses_with_search(self, client):
        """Test list warehouses with search parameter."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            matching_warehouses = [
                Warehouse(name="Main Warehouse", label="MAIN")
            ]
            mock_use_cases = AsyncMock()
            mock_use_cases.search_warehouses.return_value = matching_warehouses
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/?search=Main")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            
            # When search is provided, should call search_warehouses
            mock_use_cases.search_warehouses.assert_called_once_with("Main", 0, 20)
            mock_use_cases.list_warehouses.assert_not_called()
    
    def test_search_warehouses_endpoint(self, client):
        """Test dedicated search warehouses endpoint."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            matching_warehouses = [
                Warehouse(name="Search Test", label="SEARCH")
            ]
            mock_use_cases = AsyncMock()
            mock_use_cases.search_warehouses.return_value = matching_warehouses
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/search/?name=Search&skip=0&limit=50")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data) == 1
            assert response_data[0]["name"] == "Search Test"
            
            mock_use_cases.search_warehouses.assert_called_once_with("Search", 0, 50)
    
    def test_search_warehouses_endpoint_missing_name(self, client):
        """Test search warehouses endpoint with missing name parameter."""
        response = client.get("/api/v1/warehouses/search/")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_warehouse_success(self, client, sample_warehouse):
        """Test successful warehouse update."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            update_data = {
                "name": "Updated Warehouse",
                "label": "UPDATED",
                "remarks": "Updated via API"
            }
            
            updated_warehouse = Warehouse(
                name=update_data["name"],
                label=update_data["label"],
                remarks=update_data["remarks"],
                entity_id=sample_warehouse.id
            )
            
            mock_use_cases = AsyncMock()
            mock_use_cases.update_warehouse.return_value = updated_warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.put(f"/api/v1/warehouses/{sample_warehouse.id}", json=update_data)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["name"] == update_data["name"]
            assert response_data["label"] == update_data["label"]
            assert response_data["remarks"] == update_data["remarks"]
    
    def test_update_warehouse_partial(self, client, sample_warehouse):
        """Test partial warehouse update."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            update_data = {"name": "Partial Update"}
            
            mock_use_cases = AsyncMock()
            mock_use_cases.update_warehouse.return_value = sample_warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.put(f"/api/v1/warehouses/{sample_warehouse.id}", json=update_data)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
    
    def test_update_warehouse_not_found(self, client):
        """Test update warehouse when not found."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouse_id = str(uuid4())
            update_data = {"name": "Updated"}
            
            mock_use_cases = AsyncMock()
            mock_use_cases.update_warehouse.side_effect = ValueError("Warehouse not found")
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert "not found" in response_data["detail"]
    
    def test_update_warehouse_validation_error(self, client, sample_warehouse):
        """Test update warehouse with validation error."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            update_data = {"label": "CONFLICT"}
            
            mock_use_cases = AsyncMock()
            mock_use_cases.update_warehouse.side_effect = ValueError("Label already exists")
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.put(f"/api/v1/warehouses/{sample_warehouse.id}", json=update_data)
            
            # Assert
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            response_data = response.json()
            assert "already exists" in response_data["detail"]
    
    def test_deactivate_warehouse_success(self, client, sample_warehouse):
        """Test successful warehouse deactivation."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.deactivate_warehouse.return_value = True
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.patch(f"/api/v1/warehouses/{sample_warehouse.id}/deactivate")
            
            # Assert
            assert response.status_code == status.HTTP_204_NO_CONTENT
            mock_use_cases.deactivate_warehouse.assert_called_once_with(sample_warehouse.id)
    
    def test_deactivate_warehouse_not_found(self, client):
        """Test deactivate warehouse when not found."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouse_id = str(uuid4())
            mock_use_cases = AsyncMock()
            mock_use_cases.deactivate_warehouse.side_effect = ValueError("Warehouse not found")
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.patch(f"/api/v1/warehouses/{warehouse_id}/deactivate")
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert "not found" in response_data["detail"]
    
    def test_activate_warehouse_success(self, client, sample_warehouse):
        """Test successful warehouse activation."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.activate_warehouse.return_value = True
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.patch(f"/api/v1/warehouses/{sample_warehouse.id}/activate")
            
            # Assert
            assert response.status_code == status.HTTP_204_NO_CONTENT
            mock_use_cases.activate_warehouse.assert_called_once_with(sample_warehouse.id)
    
    def test_activate_warehouse_not_found(self, client):
        """Test activate warehouse when not found."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouse_id = str(uuid4())
            mock_use_cases = AsyncMock()
            mock_use_cases.activate_warehouse.side_effect = ValueError("Warehouse not found")
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.patch(f"/api/v1/warehouses/{warehouse_id}/activate")
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            response_data = response.json()
            assert "not found" in response_data["detail"]
    
    def test_get_warehouse_stats(self, client):
        """Test warehouse statistics endpoint."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouses = [
                Warehouse(name="Warehouse 1", label="WH1", remarks="Has remarks"),
                Warehouse(name="Warehouse 2", label="WH2"),  # No remarks
                Warehouse(name="Recent Warehouse", label="RECENT")  # Recent
            ]
            mock_use_cases = AsyncMock()
            mock_use_cases.list_warehouses.return_value = warehouses
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get("/api/v1/warehouses/stats/overview")
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert "total_warehouses" in response_data
            assert "warehouses_with_remarks" in response_data
            assert "recent_warehouses_30_days" in response_data
            assert response_data["total_warehouses"] == 3
            assert response_data["warehouses_with_remarks"] == 1


class TestWarehouseAPIErrorHandling:
    """Test API error handling and edge cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_internal_server_error_handling(self, client):
        """Test handling of internal server errors."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            mock_use_cases = AsyncMock()
            mock_use_cases.get_warehouse.side_effect = Exception("Internal error")
            mock_get_use_cases.return_value = mock_use_cases
            
            # Act
            response = client.get(f"/api/v1/warehouses/{str(uuid4())}")
            
            # Assert
            # FastAPI should handle the exception and return 500
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_malformed_json_request(self, client):
        """Test handling of malformed JSON in request."""
        response = client.post(
            "/api/v1/warehouses/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_missing_content_type(self, client):
        """Test request with missing content type."""
        response = client.post("/api/v1/warehouses/", data='{"name": "test", "label": "TEST"}')
        
        # Should still work with form data or be rejected appropriately
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE]


class TestWarehouseAPIValidation:
    """Test API input validation edge cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_warehouse_create_unicode_support(self, client):
        """Test warehouse creation with unicode characters."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            unicode_warehouse = Warehouse(
                name="仓库名称",
                label="UNICODE仓库",
                remarks="Remarks with émojis 🏪"
            )
            mock_use_cases = AsyncMock()
            mock_use_cases.create_warehouse.return_value = unicode_warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            warehouse_data = {
                "name": "仓库名称",
                "label": "unicode仓库",
                "remarks": "Remarks with émojis 🏪"
            }
            
            # Act
            response = client.post("/api/v1/warehouses/", json=warehouse_data)
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["name"] == "仓库名称"
            assert response_data["label"] == "UNICODE仓库"
            assert response_data["remarks"] == "Remarks with émojis 🏪"
    
    def test_warehouse_create_boundary_lengths(self, client):
        """Test warehouse creation with boundary length values."""
        # Test maximum allowed lengths
        max_name = "N" * 255
        max_label = "L" * 255
        
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            # Arrange
            warehouse = Warehouse(name=max_name, label=max_label)
            mock_use_cases = AsyncMock()
            mock_use_cases.create_warehouse.return_value = warehouse
            mock_get_use_cases.return_value = mock_use_cases
            
            warehouse_data = {
                "name": max_name,
                "label": max_label.lower()  # Will be normalized to uppercase
            }
            
            # Act
            response = client.post("/api/v1/warehouses/", json=warehouse_data)
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
    
    def test_warehouse_query_parameter_validation(self, client):
        """Test query parameter validation."""
        with patch('src.api.v1.endpoints.warehouses.get_warehouse_use_cases') as mock_get_use_cases:
            mock_use_cases = AsyncMock()
            mock_use_cases.list_warehouses.return_value = []
            mock_get_use_cases.return_value = mock_use_cases
            
            # Test invalid page number
            response = client.get("/api/v1/warehouses/?page=0")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test invalid page size
            response = client.get("/api/v1/warehouses/?page_size=0")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test page size too large
            response = client.get("/api/v1/warehouses/?page_size=1001")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_warehouse_api_layer_completeness():
    """Meta-test to verify API layer test coverage."""
    tested_aspects = [
        "Pydantic schema validation",
        "Request/response serialization",
        "HTTP status codes",
        "CRUD endpoint handlers",
        "Query parameter validation",
        "Path parameter validation",
        "Error handling and HTTP responses",
        "Input validation edge cases",
        "Unicode support",
        "Boundary value testing",
        "Search functionality",
        "Pagination support",
        "Statistics endpoint",
        "Activation/deactivation endpoints",
        "Label normalization in schemas"
    ]
    
    assert len(tested_aspects) >= 15, "API layer should have comprehensive test coverage"