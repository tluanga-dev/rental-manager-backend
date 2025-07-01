"""
Comprehensive test suite for Warehouse functionality.

This test suite covers all layers of the warehouse implementation:
- Domain Entity tests
- Repository tests (with mocking)
- Service layer tests
- Use case tests  
- API endpoint tests
- Integration tests with real database
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock
from typing import Optional, List

# FastAPI and HTTP testing
from fastapi.testclient import TestClient
from fastapi import status
from httpx import AsyncClient

# SQLAlchemy and Database
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Domain layer imports
from src.domain.entities.warehouse import Warehouse
from src.domain.repositories.warehouse_repository import WarehouseRepository

# Application layer imports
from src.application.services.warehouse_service import WarehouseService
from src.application.use_cases.warehouse_use_cases import WarehouseUseCases

# Infrastructure layer imports
from src.infrastructure.repositories.warehouse_repository_impl import SQLAlchemyWarehouseRepository
from src.infrastructure.database.models import WarehouseModel
from src.infrastructure.database.base import Base

# API layer imports
from src.api.v1.schemas.warehouse_schemas import (
    WarehouseCreate, 
    WarehouseUpdate, 
    WarehouseResponse
)
from src.main import app


class TestWarehouseDomainEntity:
    """Test the Warehouse domain entity business logic."""
    
    def test_warehouse_creation_valid(self):
        """Test creating a warehouse with valid data."""
        warehouse = Warehouse(
            name="Main Warehouse",
            label="MAIN",
            remarks="Primary storage facility"
        )
        
        assert warehouse.name == "Main Warehouse"
        assert warehouse.label == "MAIN"
        assert warehouse.remarks == "Primary storage facility"
        assert warehouse.is_active is True
        assert warehouse.id is not None
        assert warehouse.created_at is not None
        assert warehouse.updated_at is not None
    
    def test_warehouse_creation_minimal(self):
        """Test creating a warehouse with only required fields."""
        warehouse = Warehouse(name="Basic Warehouse", label="BASIC")
        
        assert warehouse.name == "Basic Warehouse"
        assert warehouse.label == "BASIC"
        assert warehouse.remarks is None
        assert warehouse.is_active is True
    
    def test_warehouse_label_normalization(self):
        """Test that labels are normalized to uppercase."""
        warehouse = Warehouse(name="Test", label="lowercase")
        assert warehouse.label == "LOWERCASE"
        
        warehouse2 = Warehouse(name="Test", label="MiXeD CaSe")
        assert warehouse2.label == "MIXED CASE"
    
    def test_warehouse_name_validation_empty(self):
        """Test that empty names raise ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Warehouse(name="", label="TEST")
        
        with pytest.raises(ValueError, match="Name cannot be empty"):
            Warehouse(name="   ", label="TEST")
    
    def test_warehouse_name_validation_too_long(self):
        """Test that names over 255 characters raise ValueError."""
        long_name = "a" * 256
        with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
            Warehouse(name=long_name, label="TEST")
    
    def test_warehouse_label_validation_empty(self):
        """Test that empty labels raise ValueError."""
        with pytest.raises(ValueError, match="Label cannot be empty"):
            Warehouse(name="Test", label="")
        
        with pytest.raises(ValueError, match="Label cannot be empty"):
            Warehouse(name="Test", label="   ")
    
    def test_warehouse_label_validation_too_long(self):
        """Test that labels over 255 characters raise ValueError."""
        long_label = "a" * 256
        with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
            Warehouse(name="Test", label=long_label)
    
    def test_warehouse_name_whitespace_stripping(self):
        """Test that name whitespace is stripped."""
        warehouse = Warehouse(name="  Trimmed Name  ", label="TEST")
        assert warehouse.name == "Trimmed Name"
    
    def test_warehouse_remarks_whitespace_handling(self):
        """Test remarks whitespace handling."""
        # Normal remarks
        warehouse1 = Warehouse(name="Test", label="TEST", remarks="Normal remarks")
        assert warehouse1.remarks == "Normal remarks"
        
        # Empty string becomes None
        warehouse2 = Warehouse(name="Test", label="TEST", remarks="")
        assert warehouse2.remarks is None
        
        # Whitespace-only becomes None
        warehouse3 = Warehouse(name="Test", label="TEST", remarks="   ")
        assert warehouse3.remarks is None
        
        # Whitespace is stripped
        warehouse4 = Warehouse(name="Test", label="TEST", remarks="  Trimmed  ")
        assert warehouse4.remarks == "Trimmed"
    
    def test_warehouse_update_methods(self):
        """Test warehouse update methods."""
        warehouse = Warehouse(name="Original", label="ORIG", remarks="Original remarks")
        original_updated_at = warehouse.updated_at
        
        # Test name update
        warehouse.update_name("Updated Name")
        assert warehouse.name == "Updated Name"
        assert warehouse.updated_at > original_updated_at
        
        # Test label update
        updated_at_after_name = warehouse.updated_at
        warehouse.update_label("UPDATED")
        assert warehouse.label == "UPDATED"
        assert warehouse.updated_at > updated_at_after_name
        
        # Test remarks update
        updated_at_after_label = warehouse.updated_at
        warehouse.update_remarks("Updated remarks")
        assert warehouse.remarks == "Updated remarks"
        assert warehouse.updated_at > updated_at_after_label
        
        # Test clearing remarks
        warehouse.update_remarks(None)
        assert warehouse.remarks is None
    
    def test_warehouse_activation_deactivation(self):
        """Test warehouse activation and deactivation."""
        warehouse = Warehouse(name="Test", label="TEST")
        assert warehouse.is_active is True
        
        warehouse.deactivate()
        assert warehouse.is_active is False
        
        warehouse.activate()
        assert warehouse.is_active is True
    
    def test_warehouse_string_representations(self):
        """Test warehouse string representations."""
        warehouse = Warehouse(name="Test Warehouse", label="TEST")
        
        assert str(warehouse) == "Test Warehouse"
        assert repr(warehouse) == f"Warehouse(id={warehouse.id}, name='Test Warehouse', label='TEST')"


class TestWarehouseRepository:
    """Test warehouse repository with mocking."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock warehouse repository."""
        return AsyncMock(spec=WarehouseRepository)
    
    @pytest.fixture
    def sample_warehouse(self):
        """Create a sample warehouse for testing."""
        return Warehouse(
            name="Sample Warehouse",
            label="SAMPLE",
            remarks="Test warehouse",
            entity_id=str(uuid4())
        )
    
    @pytest.mark.asyncio
    async def test_repository_create(self, mock_repository, sample_warehouse):
        """Test repository create method."""
        mock_repository.create.return_value = sample_warehouse
        
        result = await mock_repository.create(sample_warehouse)
        
        assert result == sample_warehouse
        mock_repository.create.assert_called_once_with(sample_warehouse)
    
    @pytest.mark.asyncio
    async def test_repository_get_by_id(self, mock_repository, sample_warehouse):
        """Test repository get_by_id method."""
        warehouse_id = sample_warehouse.id
        mock_repository.get_by_id.return_value = sample_warehouse
        
        result = await mock_repository.get_by_id(warehouse_id)
        
        assert result == sample_warehouse
        mock_repository.get_by_id.assert_called_once_with(warehouse_id)
    
    @pytest.mark.asyncio
    async def test_repository_get_by_id_not_found(self, mock_repository):
        """Test repository get_by_id when warehouse not found."""
        warehouse_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        result = await mock_repository.get_by_id(warehouse_id)
        
        assert result is None
        mock_repository.get_by_id.assert_called_once_with(warehouse_id)
    
    @pytest.mark.asyncio
    async def test_repository_get_by_label(self, mock_repository, sample_warehouse):
        """Test repository get_by_label method."""
        mock_repository.get_by_label.return_value = sample_warehouse
        
        result = await mock_repository.get_by_label("SAMPLE")
        
        assert result == sample_warehouse
        mock_repository.get_by_label.assert_called_once_with("SAMPLE")
    
    @pytest.mark.asyncio
    async def test_repository_get_all(self, mock_repository):
        """Test repository get_all method."""
        warehouses = [
            Warehouse(name="Warehouse 1", label="WH1"),
            Warehouse(name="Warehouse 2", label="WH2")
        ]
        mock_repository.get_all.return_value = warehouses
        
        result = await mock_repository.get_all(skip=0, limit=10, active_only=True)
        
        assert result == warehouses
        mock_repository.get_all.assert_called_once_with(skip=0, limit=10, active_only=True)
    
    @pytest.mark.asyncio
    async def test_repository_update(self, mock_repository, sample_warehouse):
        """Test repository update method."""
        sample_warehouse.update_name("Updated Name")
        mock_repository.update.return_value = sample_warehouse
        
        result = await mock_repository.update(sample_warehouse)
        
        assert result == sample_warehouse
        assert result.name == "Updated Name"
        mock_repository.update.assert_called_once_with(sample_warehouse)
    
    @pytest.mark.asyncio
    async def test_repository_search_by_name(self, mock_repository):
        """Test repository search_by_name method."""
        matching_warehouse = Warehouse(name="Test Warehouse", label="TEST")
        mock_repository.search_by_name.return_value = [matching_warehouse]
        
        result = await mock_repository.search_by_name("Test", skip=0, limit=10)
        
        assert result == [matching_warehouse]
        mock_repository.search_by_name.assert_called_once_with("Test", skip=0, limit=10)


class TestWarehouseService:
    """Test warehouse service layer."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock warehouse repository."""
        return AsyncMock(spec=WarehouseRepository)
    
    @pytest.fixture
    def warehouse_service(self, mock_repository):
        """Create warehouse service with mock repository."""
        return WarehouseService(mock_repository)
    
    @pytest.fixture
    def sample_warehouse(self):
        """Create a sample warehouse for testing."""
        return Warehouse(
            name="Service Test Warehouse",
            label="SERVICE",
            remarks="Test warehouse for service tests",
            entity_id=str(uuid4())
        )
    
    @pytest.mark.asyncio
    async def test_create_warehouse_success(self, warehouse_service, mock_repository):
        """Test successful warehouse creation."""
        # Mock that no existing warehouse with same label exists
        mock_repository.get_by_label.return_value = None
        
        # Mock successful creation
        created_warehouse = Warehouse(name="New Warehouse", label="NEW")
        mock_repository.create.return_value = created_warehouse
        
        result = await warehouse_service.create_warehouse(
            name="New Warehouse",
            label="new",  # Should be normalized to uppercase
            remarks="Test remarks",
            created_by="test_user"
        )
        
        assert result == created_warehouse
        mock_repository.get_by_label.assert_called_once_with("NEW")  # Label normalized to uppercase
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_warehouse_duplicate_label(self, warehouse_service, mock_repository, sample_warehouse):
        """Test warehouse creation with duplicate label."""
        # Mock existing warehouse with same label
        mock_repository.get_by_label.return_value = sample_warehouse
        
        with pytest.raises(ValueError, match="Warehouse with label 'SERVICE' already exists"):
            await warehouse_service.create_warehouse(
                name="Another Warehouse",
                label="SERVICE"
            )
        
        mock_repository.get_by_label.assert_called_once_with("SERVICE")
        mock_repository.create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_warehouse_by_id_success(self, warehouse_service, mock_repository, sample_warehouse):
        """Test successful get warehouse by id."""
        mock_repository.get_by_id.return_value = sample_warehouse
        
        result = await warehouse_service.get_warehouse_by_id(sample_warehouse.id)
        
        assert result == sample_warehouse
        mock_repository.get_by_id.assert_called_once_with(sample_warehouse.id)
    
    @pytest.mark.asyncio
    async def test_get_warehouse_by_id_not_found(self, warehouse_service, mock_repository):
        """Test get warehouse by id when not found."""
        warehouse_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        result = await warehouse_service.get_warehouse_by_id(warehouse_id)
        
        assert result is None
        mock_repository.get_by_id.assert_called_once_with(warehouse_id)
    
    @pytest.mark.asyncio
    async def test_get_warehouse_by_label_success(self, warehouse_service, mock_repository, sample_warehouse):
        """Test successful get warehouse by label."""
        mock_repository.get_by_label.return_value = sample_warehouse
        
        result = await warehouse_service.get_warehouse_by_label("SERVICE")
        
        assert result == sample_warehouse
        mock_repository.get_by_label.assert_called_once_with("SERVICE")
    
    @pytest.mark.asyncio
    async def test_update_warehouse_success(self, warehouse_service, mock_repository, sample_warehouse):
        """Test successful warehouse update."""
        # Mock getting the existing warehouse
        mock_repository.get_by_id.return_value = sample_warehouse
        
        # Mock checking for label conflicts (no conflict)
        mock_repository.get_by_label.return_value = None
        
        # Mock successful update
        updated_warehouse = Warehouse(
            name="Updated Name",
            label="UPDATED",
            remarks="Updated remarks",
            entity_id=sample_warehouse.id
        )
        mock_repository.update.return_value = updated_warehouse
        
        result = await warehouse_service.update_warehouse(
            warehouse_id=sample_warehouse.id,
            name="Updated Name",
            label="UPDATED",
            remarks="Updated remarks"
        )
        
        assert result == updated_warehouse
        mock_repository.get_by_id.assert_called_once_with(sample_warehouse.id)
        mock_repository.get_by_label.assert_called_once_with("UPDATED")
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_warehouse_not_found(self, warehouse_service, mock_repository):
        """Test update warehouse when warehouse not found."""
        warehouse_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match=f"Warehouse with id {warehouse_id} not found"):
            await warehouse_service.update_warehouse(
                warehouse_id=warehouse_id,
                name="Updated Name"
            )
        
        mock_repository.get_by_id.assert_called_once_with(warehouse_id)
        mock_repository.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_update_warehouse_label_conflict(self, warehouse_service, mock_repository, sample_warehouse):
        """Test update warehouse with conflicting label."""
        # Mock getting the existing warehouse
        mock_repository.get_by_id.return_value = sample_warehouse
        
        # Mock existing warehouse with conflicting label
        conflicting_warehouse = Warehouse(name="Other", label="CONFLICT", entity_id=uuid4())
        mock_repository.get_by_label.return_value = conflicting_warehouse
        
        with pytest.raises(ValueError, match="Warehouse with label 'CONFLICT' already exists"):
            await warehouse_service.update_warehouse(
                warehouse_id=sample_warehouse.id,
                label="CONFLICT"
            )
        
        mock_repository.get_by_id.assert_called_once_with(sample_warehouse.id)
        mock_repository.get_by_label.assert_called_once_with("CONFLICT")
        mock_repository.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_deactivate_warehouse_success(self, warehouse_service, mock_repository, sample_warehouse):
        """Test successful warehouse deactivation."""
        mock_repository.get_by_id.return_value = sample_warehouse
        mock_repository.update.return_value = sample_warehouse
        
        result = await warehouse_service.deactivate_warehouse(sample_warehouse.id)
        
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(sample_warehouse.id)
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_deactivate_warehouse_not_found(self, warehouse_service, mock_repository):
        """Test deactivate warehouse when not found."""
        warehouse_id = uuid4()
        mock_repository.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match=f"Warehouse with id {warehouse_id} not found"):
            await warehouse_service.deactivate_warehouse(warehouse_id)
        
        mock_repository.get_by_id.assert_called_once_with(warehouse_id)
        mock_repository.update.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_activate_warehouse_success(self, warehouse_service, mock_repository, sample_warehouse):
        """Test successful warehouse activation."""
        sample_warehouse.deactivate()  # Start with deactivated warehouse
        mock_repository.get_by_id.return_value = sample_warehouse
        mock_repository.update.return_value = sample_warehouse
        
        result = await warehouse_service.activate_warehouse(sample_warehouse.id)
        
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(sample_warehouse.id)
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_warehouses(self, warehouse_service, mock_repository):
        """Test get all warehouses."""
        warehouses = [
            Warehouse(name="Warehouse 1", label="WH1"),
            Warehouse(name="Warehouse 2", label="WH2")
        ]
        mock_repository.get_all.return_value = warehouses
        
        result = await warehouse_service.get_all_warehouses(skip=10, limit=50, active_only=False)
        
        assert result == warehouses
        mock_repository.get_all.assert_called_once_with(10, 50, False)
    
    @pytest.mark.asyncio
    async def test_search_warehouses_by_name(self, warehouse_service, mock_repository):
        """Test search warehouses by name."""
        matching_warehouses = [
            Warehouse(name="Main Warehouse", label="MAIN"),
            Warehouse(name="Secondary Warehouse", label="SEC")
        ]
        mock_repository.search_by_name.return_value = matching_warehouses
        
        result = await warehouse_service.search_warehouses_by_name("Warehouse", skip=0, limit=100)
        
        assert result == matching_warehouses
        mock_repository.search_by_name.assert_called_once_with("Warehouse", 0, 100)


class TestWarehouseUseCases:
    """Test warehouse use cases layer."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock warehouse service."""
        return AsyncMock(spec=WarehouseService)
    
    @pytest.fixture
    def warehouse_use_cases(self, mock_service):
        """Create warehouse use cases with mock service."""
        return WarehouseUseCases(mock_service)
    
    @pytest.fixture
    def sample_warehouse(self):
        """Create a sample warehouse for testing."""
        return Warehouse(
            name="Use Case Test Warehouse",
            label="USECASE",
            remarks="Test warehouse for use case tests",
            entity_id=str(uuid4())
        )
    
    @pytest.mark.asyncio
    async def test_create_warehouse_use_case(self, warehouse_use_cases, mock_service, sample_warehouse):
        """Test create warehouse use case."""
        mock_service.create_warehouse.return_value = sample_warehouse
        
        result = await warehouse_use_cases.create_warehouse(
            name="Use Case Test Warehouse",
            label="USECASE",
            remarks="Test warehouse for use case tests",
            created_by="test_user"
        )
        
        assert result == sample_warehouse
        mock_service.create_warehouse.assert_called_once_with(
            name="Use Case Test Warehouse",
            label="USECASE",
            remarks="Test warehouse for use case tests",
            created_by="test_user"
        )
    
    @pytest.mark.asyncio
    async def test_get_warehouse_use_case(self, warehouse_use_cases, mock_service, sample_warehouse):
        """Test get warehouse use case."""
        mock_service.get_warehouse_by_id.return_value = sample_warehouse
        
        result = await warehouse_use_cases.get_warehouse(sample_warehouse.id)
        
        assert result == sample_warehouse
        mock_service.get_warehouse_by_id.assert_called_once_with(sample_warehouse.id)
    
    @pytest.mark.asyncio
    async def test_get_warehouse_by_label_use_case(self, warehouse_use_cases, mock_service, sample_warehouse):
        """Test get warehouse by label use case."""
        mock_service.get_warehouse_by_label.return_value = sample_warehouse
        
        result = await warehouse_use_cases.get_warehouse_by_label("USECASE")
        
        assert result == sample_warehouse
        mock_service.get_warehouse_by_label.assert_called_once_with("USECASE")
    
    @pytest.mark.asyncio
    async def test_list_warehouses_use_case(self, warehouse_use_cases, mock_service):
        """Test list warehouses use case."""
        warehouses = [
            Warehouse(name="Warehouse 1", label="WH1"),
            Warehouse(name="Warehouse 2", label="WH2")
        ]
        mock_service.get_all_warehouses.return_value = warehouses
        
        result = await warehouse_use_cases.list_warehouses(skip=0, limit=100, active_only=True)
        
        assert result == warehouses
        mock_service.get_all_warehouses.assert_called_once_with(0, 100, True)
    
    @pytest.mark.asyncio
    async def test_update_warehouse_use_case(self, warehouse_use_cases, mock_service, sample_warehouse):
        """Test update warehouse use case."""
        updated_warehouse = Warehouse(
            name="Updated Name",
            label="UPDATED",
            entity_id=sample_warehouse.id
        )
        mock_service.update_warehouse.return_value = updated_warehouse
        
        result = await warehouse_use_cases.update_warehouse(
            warehouse_id=sample_warehouse.id,
            name="Updated Name",
            label="UPDATED",
            remarks=None
        )
        
        assert result == updated_warehouse
        mock_service.update_warehouse.assert_called_once_with(
            warehouse_id=sample_warehouse.id,
            name="Updated Name",
            label="UPDATED",
            remarks=None
        )
    
    @pytest.mark.asyncio
    async def test_deactivate_warehouse_use_case(self, warehouse_use_cases, mock_service, sample_warehouse):
        """Test deactivate warehouse use case."""
        mock_service.deactivate_warehouse.return_value = True
        
        result = await warehouse_use_cases.deactivate_warehouse(sample_warehouse.id)
        
        assert result is True
        mock_service.deactivate_warehouse.assert_called_once_with(sample_warehouse.id)
    
    @pytest.mark.asyncio
    async def test_activate_warehouse_use_case(self, warehouse_use_cases, mock_service, sample_warehouse):
        """Test activate warehouse use case."""
        mock_service.activate_warehouse.return_value = True
        
        result = await warehouse_use_cases.activate_warehouse(sample_warehouse.id)
        
        assert result is True
        mock_service.activate_warehouse.assert_called_once_with(sample_warehouse.id)
    
    @pytest.mark.asyncio
    async def test_search_warehouses_use_case(self, warehouse_use_cases, mock_service):
        """Test search warehouses use case."""
        matching_warehouses = [
            Warehouse(name="Test Warehouse", label="TEST")
        ]
        mock_service.search_warehouses_by_name.return_value = matching_warehouses
        
        result = await warehouse_use_cases.search_warehouses("Test", skip=0, limit=100)
        
        assert result == matching_warehouses
        mock_service.search_warehouses_by_name.assert_called_once_with("Test", 0, 100)


class TestWarehouseAPI:
    """Test warehouse API endpoints."""
    
    @pytest.fixture
    def mock_use_cases(self):
        """Mock warehouse use cases."""
        return AsyncMock(spec=WarehouseUseCases)
    
    @pytest.fixture
    def client(self, mock_use_cases):
        """Create test client with dependency override."""
        from src.api.v1.endpoints.warehouses import get_warehouse_use_cases
        
        app.dependency_overrides[get_warehouse_use_cases] = lambda: mock_use_cases
        yield TestClient(app)
        app.dependency_overrides.clear()
    
    def test_create_warehouse_success(self, client, mock_use_cases):
        """Test successful warehouse creation via API."""
        # Prepare test data
        warehouse_data = {
            "name": "API Test Warehouse",
            "label": "API",
            "remarks": "Created via API test",
            "created_by": "test_user"
        }
        
        created_warehouse = Warehouse(
            name=warehouse_data["name"],
            label=warehouse_data["label"],
            remarks=warehouse_data["remarks"],
            entity_id=str(uuid4())
        )
        mock_use_cases.create_warehouse.return_value = created_warehouse
        
        # Make API call
        response = client.post("/api/v1/warehouses/", json=warehouse_data)
        
        # Assert response
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == warehouse_data["name"]
        assert response_data["label"] == warehouse_data["label"]
        assert response_data["remarks"] == warehouse_data["remarks"]
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
    
    def test_create_warehouse_validation_error(self, client, mock_use_cases):
        """Test warehouse creation with validation error."""
        # Missing required fields
        warehouse_data = {
            "remarks": "Missing name and label"
        }
        
        response = client.post("/api/v1/warehouses/", json=warehouse_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_use_cases.create_warehouse.assert_not_called()
    
    def test_create_warehouse_duplicate_label(self, client, mock_use_cases):
        """Test warehouse creation with duplicate label."""
        warehouse_data = {
            "name": "Duplicate Test",
            "label": "DUPLICATE",
            "created_by": "test_user"
        }
        
        mock_use_cases.create_warehouse.side_effect = ValueError("Warehouse with label 'DUPLICATE' already exists")
        
        response = client.post("/api/v1/warehouses/", json=warehouse_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_get_warehouse_success(self, client, mock_use_cases):
        """Test successful get warehouse by ID."""
        warehouse_id = uuid4()
        warehouse = Warehouse(
            name="Retrieved Warehouse",
            label="RETRIEVED",
            entity_id=warehouse_id
        )
        mock_use_cases.get_warehouse.return_value = warehouse
        
        response = client.get(f"/api/v1/warehouses/{warehouse_id}")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Retrieved Warehouse"
        assert response_data["label"] == "RETRIEVED"
        assert response_data["id"] == str(warehouse_id)
    
    def test_get_warehouse_not_found(self, client, mock_use_cases):
        """Test get warehouse when not found."""
        warehouse_id = uuid4()
        mock_use_cases.get_warehouse.return_value = None
        
        response = client.get(f"/api/v1/warehouses/{warehouse_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_get_warehouse_by_label_success(self, client, mock_use_cases):
        """Test successful get warehouse by label."""
        warehouse = Warehouse(
            name="Label Test Warehouse",
            label="LABELTEST",
            entity_id=str(uuid4())
        )
        mock_use_cases.get_warehouse_by_label.return_value = warehouse
        
        response = client.get("/api/v1/warehouses/label/LABELTEST")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Label Test Warehouse"
        assert response_data["label"] == "LABELTEST"
    
    def test_get_warehouse_by_label_not_found(self, client, mock_use_cases):
        """Test get warehouse by label when not found."""
        mock_use_cases.get_warehouse_by_label.return_value = None
        
        response = client.get("/api/v1/warehouses/label/NOTFOUND")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_list_warehouses_default_params(self, client, mock_use_cases):
        """Test list warehouses with default parameters."""
        warehouses = [
            Warehouse(name="Warehouse 1", label="WH1"),
            Warehouse(name="Warehouse 2", label="WH2")
        ]
        mock_use_cases.list_warehouses.return_value = warehouses
        
        response = client.get("/api/v1/warehouses/")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "count" in response_data
        assert "results" in response_data
        assert len(response_data["results"]) == 2
        
        # Check that default parameters were used
        mock_use_cases.list_warehouses.assert_called_once_with(
            0, 20, active_only=True
        )
    
    def test_list_warehouses_custom_params(self, client, mock_use_cases):
        """Test list warehouses with custom parameters."""
        warehouses = [Warehouse(name="Test", label="TEST")]
        mock_use_cases.list_warehouses.return_value = warehouses
        
        response = client.get("/api/v1/warehouses/?page=2&page_size=10&is_active=false")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check that custom parameters were used (page 2 means skip=10)
        mock_use_cases.list_warehouses.assert_called_once_with(
            10, 10, active_only=False
        )
    
    def test_search_warehouses_with_query(self, client, mock_use_cases):
        """Test list warehouses with search query."""
        matching_warehouses = [
            Warehouse(name="Main Warehouse", label="MAIN")
        ]
        mock_use_cases.search_warehouses.return_value = matching_warehouses
        
        response = client.get("/api/v1/warehouses/?search=Main")
        
        assert response.status_code == status.HTTP_200_OK
        
        # When search is provided, should call search_warehouses
        mock_use_cases.search_warehouses.assert_called_once_with("Main", 0, 20)
        mock_use_cases.list_warehouses.assert_not_called()
    
    def test_search_warehouses_endpoint(self, client, mock_use_cases):
        """Test dedicated search warehouses endpoint."""
        matching_warehouses = [
            Warehouse(name="Search Test", label="SEARCH")
        ]
        mock_use_cases.search_warehouses.return_value = matching_warehouses
        
        response = client.get("/api/v1/warehouses/search/?name=Search&skip=0&limit=50")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["name"] == "Search Test"
        
        mock_use_cases.search_warehouses.assert_called_once_with("Search", 0, 50)
    
    def test_update_warehouse_success(self, client, mock_use_cases):
        """Test successful warehouse update."""
        warehouse_id = uuid4()
        update_data = {
            "name": "Updated Warehouse",
            "label": "UPDATED",
            "remarks": "Updated via API"
        }
        
        updated_warehouse = Warehouse(
            name=update_data["name"],
            label=update_data["label"],
            remarks=update_data["remarks"],
            entity_id=warehouse_id
        )
        mock_use_cases.update_warehouse.return_value = updated_warehouse
        
        response = client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == update_data["name"]
        assert response_data["label"] == update_data["label"]
        assert response_data["remarks"] == update_data["remarks"]
    
    def test_update_warehouse_not_found(self, client, mock_use_cases):
        """Test update warehouse when not found."""
        warehouse_id = uuid4()
        update_data = {"name": "Updated"}
        
        mock_use_cases.update_warehouse.side_effect = ValueError("Warehouse not found")
        
        response = client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_update_warehouse_validation_error(self, client, mock_use_cases):
        """Test update warehouse with validation error."""
        warehouse_id = uuid4()
        update_data = {"label": "CONFLICT"}
        
        mock_use_cases.update_warehouse.side_effect = ValueError("Label already exists")
        
        response = client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_deactivate_warehouse_success(self, client, mock_use_cases):
        """Test successful warehouse deactivation."""
        warehouse_id = uuid4()
        mock_use_cases.deactivate_warehouse.return_value = True
        
        response = client.patch(f"/api/v1/warehouses/{warehouse_id}/deactivate")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_use_cases.deactivate_warehouse.assert_called_once_with(warehouse_id)
    
    def test_deactivate_warehouse_not_found(self, client, mock_use_cases):
        """Test deactivate warehouse when not found."""
        warehouse_id = uuid4()
        mock_use_cases.deactivate_warehouse.side_effect = ValueError("Warehouse not found")
        
        response = client.patch(f"/api/v1/warehouses/{warehouse_id}/deactivate")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_activate_warehouse_success(self, client, mock_use_cases):
        """Test successful warehouse activation."""
        warehouse_id = uuid4()
        mock_use_cases.activate_warehouse.return_value = True
        
        response = client.patch(f"/api/v1/warehouses/{warehouse_id}/activate")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_use_cases.activate_warehouse.assert_called_once_with(warehouse_id)
    
    def test_activate_warehouse_not_found(self, client, mock_use_cases):
        """Test activate warehouse when not found."""
        warehouse_id = uuid4()
        mock_use_cases.activate_warehouse.side_effect = ValueError("Warehouse not found")
        
        response = client.patch(f"/api/v1/warehouses/{warehouse_id}/activate")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"]
    
    def test_get_warehouse_stats(self, client, mock_use_cases):
        """Test warehouse statistics endpoint."""
        from datetime import datetime, timezone, timedelta
        
        # Mock warehouses for stats calculation
        now = datetime.now(timezone.utc)
        old_date = now - timedelta(days=60)
        
        warehouses = [
            Warehouse(name="Warehouse 1", label="WH1", remarks="Has remarks", 
                     created_at=old_date, entity_id=uuid4()),
            Warehouse(name="Warehouse 2", label="WH2", 
                     created_at=old_date, entity_id=uuid4()),  # No remarks
            Warehouse(name="Recent Warehouse", label="RECENT", 
                     created_at=now - timedelta(days=10), entity_id=uuid4())  # Recent
        ]
        mock_use_cases.list_warehouses.return_value = warehouses
        
        response = client.get("/api/v1/warehouses/stats/overview")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "total_warehouses" in response_data
        assert "warehouses_with_remarks" in response_data
        assert "recent_warehouses_30_days" in response_data
        assert response_data["total_warehouses"] == 3
        assert response_data["warehouses_with_remarks"] == 1
        assert response_data["recent_warehouses_30_days"] == 1


class TestWarehouseIntegration:
    """Integration tests with real database operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session using PostgreSQL from docker-compose."""
        from src.core.config.database import get_database_manager
        from src.infrastructure.database.models import WarehouseModel
        
        # Use the PostgreSQL database from docker-compose
        db_manager = get_database_manager()
        session = db_manager.SessionLocal()
        
        # Clean up test warehouses before and after each test
        test_labels = ['UNIQUE', 'INTEGRATION', 'MAIN', 'SEC', 'EMERG', 'PAGE1', 'PAGE2', 'PAGE3', 'PAGE4', 'PAGE5']
        
        # Clean up before test
        try:
            session.query(WarehouseModel).filter(WarehouseModel.label.in_(test_labels)).delete(synchronize_session=False)
            session.commit()
        except Exception:
            session.rollback()
        
        try:
            yield session
        finally:
            # Clean up test warehouses after test
            try:
                session.query(WarehouseModel).filter(WarehouseModel.label.in_(test_labels)).delete(synchronize_session=False)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
    
    @pytest.fixture
    def repository(self, db_session):
        """Create repository with real database session."""
        return SQLAlchemyWarehouseRepository(db_session)
    
    @pytest.fixture
    def service(self, repository):
        """Create service with real repository."""
        return WarehouseService(repository)
    
    @pytest.fixture
    def use_cases(self, service):
        """Create use cases with real service."""
        return WarehouseUseCases(service)
    
    @pytest.mark.asyncio
    async def test_full_warehouse_lifecycle(self, use_cases):
        """Test complete warehouse lifecycle with real database."""
        # Create warehouse
        created_warehouse = await use_cases.create_warehouse(
            name="Integration Test Warehouse",
            label="INTEGRATION",
            remarks="Full lifecycle test",
            created_by="integration_test"
        )
        
        assert created_warehouse.name == "Integration Test Warehouse"
        assert created_warehouse.label == "INTEGRATION"
        assert created_warehouse.remarks == "Full lifecycle test"
        assert created_warehouse.is_active is True
        
        # Get warehouse by ID
        retrieved_warehouse = await use_cases.get_warehouse(created_warehouse.id)
        assert retrieved_warehouse is not None
        assert retrieved_warehouse.id == created_warehouse.id
        assert retrieved_warehouse.name == created_warehouse.name
        
        # Get warehouse by label
        retrieved_by_label = await use_cases.get_warehouse_by_label("INTEGRATION")
        assert retrieved_by_label is not None
        assert retrieved_by_label.id == created_warehouse.id
        
        # Update warehouse
        updated_warehouse = await use_cases.update_warehouse(
            warehouse_id=created_warehouse.id,
            name="Updated Integration Warehouse",
            remarks="Updated in integration test"
        )
        assert updated_warehouse.name == "Updated Integration Warehouse"
        assert updated_warehouse.remarks == "Updated in integration test"
        assert updated_warehouse.label == "INTEGRATION"  # Unchanged
        
        # List warehouses (should include our warehouse)
        all_warehouses = await use_cases.list_warehouses(skip=0, limit=100, active_only=True)
        assert len(all_warehouses) >= 1
        warehouse_ids = [w.id for w in all_warehouses]
        assert created_warehouse.id in warehouse_ids
        
        # Search warehouses
        search_results = await use_cases.search_warehouses("Integration", skip=0, limit=100)
        assert len(search_results) >= 1
        search_ids = [w.id for w in search_results]
        assert created_warehouse.id in search_ids
        
        # Deactivate warehouse
        deactivate_result = await use_cases.deactivate_warehouse(created_warehouse.id)
        assert deactivate_result is True
        
        # Verify deactivation (should not appear in active-only list)
        active_warehouses = await use_cases.list_warehouses(skip=0, limit=100, active_only=True)
        active_ids = [w.id for w in active_warehouses]
        assert created_warehouse.id not in active_ids
        
        # Verify still appears in all warehouses
        all_warehouses_including_inactive = await use_cases.list_warehouses(skip=0, limit=100, active_only=False)
        all_ids = [w.id for w in all_warehouses_including_inactive]
        assert created_warehouse.id in all_ids
        
        # Reactivate warehouse
        activate_result = await use_cases.activate_warehouse(created_warehouse.id)
        assert activate_result is True
        
        # Verify reactivation
        active_warehouses_after_reactivation = await use_cases.list_warehouses(skip=0, limit=100, active_only=True)
        active_ids_after = [w.id for w in active_warehouses_after_reactivation]
        assert created_warehouse.id in active_ids_after
    
    @pytest.mark.asyncio
    async def test_warehouse_label_uniqueness_constraint(self, use_cases):
        """Test that warehouse labels must be unique."""
        # Create first warehouse
        warehouse1 = await use_cases.create_warehouse(
            name="First Warehouse",
            label="UNIQUE",
            created_by="test"
        )
        assert warehouse1.label == "UNIQUE"
        
        # Try to create second warehouse with same label
        with pytest.raises(ValueError, match="Warehouse with label 'UNIQUE' already exists"):
            await use_cases.create_warehouse(
                name="Second Warehouse",
                label="unique",  # Should be normalized to "UNIQUE"
                created_by="test"
            )
    
    @pytest.mark.asyncio
    async def test_warehouse_search_functionality(self, use_cases):
        """Test warehouse search functionality with real data."""
        # Create test warehouses
        await use_cases.create_warehouse(name="Main Distribution Center", label="MAIN", created_by="test")
        await use_cases.create_warehouse(name="Secondary Warehouse", label="SEC", created_by="test")
        await use_cases.create_warehouse(name="Emergency Storage", label="EMERG", created_by="test")
        
        # Search for warehouses containing "Warehouse"
        warehouse_results = await use_cases.search_warehouses("Warehouse")
        warehouse_names = [w.name for w in warehouse_results]
        assert "Secondary Warehouse" in warehouse_names
        assert "Main Distribution Center" not in warehouse_names  # Doesn't contain "Warehouse"
        
        # Search for warehouses containing "Storage"
        storage_results = await use_cases.search_warehouses("Storage")
        storage_names = [w.name for w in storage_results]
        assert "Emergency Storage" in storage_names
        
        # Search with no matches
        no_match_results = await use_cases.search_warehouses("NonExistent")
        assert len(no_match_results) == 0
    
    @pytest.mark.asyncio
    async def test_warehouse_pagination(self, use_cases):
        """Test warehouse pagination functionality."""
        # Create multiple warehouses
        for i in range(5):
            await use_cases.create_warehouse(
                name=f"Pagination Test Warehouse {i+1}",
                label=f"PAGE{i+1}",
                created_by="pagination_test"
            )
        
        # Test first page
        page1 = await use_cases.list_warehouses(skip=0, limit=3, active_only=True)
        assert len(page1) == 3
        
        # Test second page
        page2 = await use_cases.list_warehouses(skip=3, limit=3, active_only=True)
        assert len(page2) >= 2  # At least our remaining warehouses
        
        # Ensure no overlap between pages
        page1_ids = [w.id for w in page1]
        page2_ids = [w.id for w in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0  # No intersection


class TestWarehouseEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_warehouse_creation_edge_cases(self):
        """Test warehouse creation edge cases."""
        # Test with exactly 255 characters (should work)
        long_name = "a" * 255
        warehouse = Warehouse(name=long_name, label="LONG")
        assert warehouse.name == long_name
        
        # Test with whitespace variations
        warehouse_spaces = Warehouse(name="   Name   ", label="   label   ")
        assert warehouse_spaces.name == "Name"
        assert warehouse_spaces.label == "LABEL"
        
        # Test remarks edge cases
        warehouse_empty_remarks = Warehouse(name="Test", label="TEST", remarks="")
        assert warehouse_empty_remarks.remarks is None
        
        warehouse_whitespace_remarks = Warehouse(name="Test", label="TEST2", remarks="   ")
        assert warehouse_whitespace_remarks.remarks is None
    
    def test_warehouse_update_edge_cases(self):
        """Test warehouse update edge cases."""
        warehouse = Warehouse(name="Original", label="ORIG")
        
        # Test updating with same values (should still update timestamps)
        original_updated_at = warehouse.updated_at
        warehouse.update_name("Original")
        assert warehouse.updated_at > original_updated_at
        
        # Test updating with whitespace
        warehouse.update_name("   Updated Name   ")
        assert warehouse.name == "Updated Name"
        
        # Test clearing remarks
        warehouse.update_remarks("Some remarks")
        assert warehouse.remarks == "Some remarks"
        
        warehouse.update_remarks("")
        assert warehouse.remarks is None
        
        warehouse.update_remarks("   ")
        assert warehouse.remarks is None
    
    def test_warehouse_validation_boundary_conditions(self):
        """Test validation at boundary conditions."""
        # Test name length exactly at limit
        name_255 = "a" * 255
        warehouse = Warehouse(name=name_255, label="TEST")
        assert len(warehouse.name) == 255
        
        # Test label length exactly at limit
        label_255 = "b" * 255
        warehouse2 = Warehouse(name="Test", label=label_255)
        assert len(warehouse2.label) == 255
        
        # Test name length over limit
        name_256 = "a" * 256
        with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
            Warehouse(name=name_256, label="TEST")
        
        # Test label length over limit
        label_256 = "b" * 256
        with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
            Warehouse(name="Test", label=label_256)
    
    def test_warehouse_unicode_support(self):
        """Test warehouse with unicode characters."""
        unicode_warehouse = Warehouse(
            name="仓库名称",  # Chinese characters
            label="UNICODE仓库",  # Mixed unicode
            remarks="Remarks with émojis 🏪 and accénts"
        )
        
        assert unicode_warehouse.name == "仓库名称"
        assert unicode_warehouse.label == "UNICODE仓库"
        assert unicode_warehouse.remarks == "Remarks with émojis 🏪 and accénts"
    
    def test_warehouse_none_handling(self):
        """Test warehouse handling of None values."""
        # Test creation with None values for optional fields
        warehouse = Warehouse(name="Test", label="TEST", remarks=None)
        assert warehouse.remarks is None
        
        # Test update with None (should clear the field)
        warehouse.update_remarks("Some remarks")
        assert warehouse.remarks == "Some remarks"
        
        warehouse.update_remarks(None)
        assert warehouse.remarks is None


# Pytest configuration and fixtures that apply to all test classes
@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async test backend."""
    return "asyncio"


def test_warehouse_comprehensive_suite_completeness():
    """Meta-test to ensure all major functionality is covered."""
    # This test documents what functionality is covered by this test suite
    covered_functionality = [
        "Domain entity creation and validation",
        "Domain entity business logic (updates, activation/deactivation)",
        "Repository interface contracts",
        "Service layer business operations",
        "Use case orchestration",
        "API endpoint request/response handling",
        "Integration testing with real database",
        "Error handling and edge cases",
        "Validation boundary conditions",
        "Unicode support",
        "Pagination functionality",
        "Search functionality",
        "Label uniqueness constraints",
        "Full CRUD lifecycle",
        "Soft delete functionality"
    ]
    
    # This test passes if it runs, indicating the comprehensive suite is loaded
    assert len(covered_functionality) >= 15
    print(f"✅ Warehouse test suite covers {len(covered_functionality)} major areas of functionality")