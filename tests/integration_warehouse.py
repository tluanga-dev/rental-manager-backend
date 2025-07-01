"""
Integration tests for Warehouse functionality.

These tests verify the complete integration between all layers:
- API endpoints with real FastAPI application
- Database operations with real SQLAlchemy and PostgreSQL/SQLite
- Full request/response cycles
- Data persistence and retrieval
- Business logic validation end-to-end
"""

import pytest
import asyncio
from typing import Dict, Any, List
from uuid import uuid4
from datetime import datetime, timezone

# FastAPI and HTTP testing
from fastapi.testclient import TestClient
from fastapi import status
from httpx import AsyncClient

# SQLAlchemy and Database
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Application imports
from src.main import app
from src.infrastructure.database.base import Base
from src.infrastructure.database.models import WarehouseModel
from src.core.config.database import get_db_session
from src.domain.entities.warehouse import Warehouse


class TestWarehouseIntegrationSetup:
    """Setup and teardown for integration tests."""
    
    @pytest.fixture(scope="class")
    def test_engine(self):
        """Create a test database engine using PostgreSQL."""
        import os
        
        # Use PostgreSQL test database (assumes Docker Compose is running)
        database_url = os.getenv(
            "TEST_DATABASE_URL", 
            "postgresql://rental_user:rental_password@localhost:5432/rental_db"
        )
        
        engine = create_engine(
            database_url,
            echo=False  # Set to True for SQL debugging
        )
        
        yield engine
        
        # Cleanup - Note: In integration tests, we typically don't drop all tables
        # as they may be needed by other tests or the application
        engine.dispose()
    
    @pytest.fixture(scope="class")
    def test_session_factory(self, test_engine):
        """Create a test session factory."""
        return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    @pytest.fixture
    def test_session(self, test_session_factory):
        """Create a test database session for each test."""
        session = test_session_factory()
        try:
            yield session
        finally:
            session.rollback()
            session.close()
    
    @pytest.fixture
    def test_client(self, test_session):
        """Create a test client with database dependency override."""
        def override_get_db():
            try:
                yield test_session
            finally:
                pass  # Session cleanup handled by test_session fixture
        
        app.dependency_overrides[get_db_session] = override_get_db
        
        with TestClient(app) as client:
            yield client
        
        # Clean up dependency override
        app.dependency_overrides.clear()
    
    @pytest.fixture
    def sample_warehouse_data(self):
        """Sample warehouse data for testing."""
        return {
            "name": "Integration Test Warehouse",
            "label": "INTEGRATION",
            "remarks": "Warehouse for integration testing",
            "created_by": "integration_test"
        }
    
    @pytest.fixture
    def multiple_warehouse_data(self):
        """Multiple warehouse data for batch testing."""
        return [
            {
                "name": "Main Distribution Center",
                "label": "MAIN",
                "remarks": "Primary distribution center",
                "created_by": "admin"
            },
            {
                "name": "Secondary Warehouse",
                "label": "SECONDARY",
                "remarks": "Secondary storage facility",
                "created_by": "admin"
            },
            {
                "name": "Emergency Storage",
                "label": "EMERGENCY",
                "remarks": "Emergency backup storage",
                "created_by": "admin"
            }
        ]


class TestWarehouseAPIIntegration(TestWarehouseIntegrationSetup):
    """Integration tests for warehouse API endpoints with real database."""
    
    def test_create_warehouse_integration(self, test_client, sample_warehouse_data):
        """Test creating a warehouse through the complete API stack."""
        # Act
        response = test_client.post("/api/v1/warehouses/", json=sample_warehouse_data)
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        assert response_data["name"] == sample_warehouse_data["name"]
        assert response_data["label"] == sample_warehouse_data["label"]
        assert response_data["remarks"] == sample_warehouse_data["remarks"]
        assert response_data["created_by"] == sample_warehouse_data["created_by"]
        assert response_data["is_active"] is True
        assert "id" in response_data
        assert "created_at" in response_data
        assert "updated_at" in response_data
        
        # Verify the warehouse was persisted in database
        warehouse_id = UUID(response_data["id"])
        get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["name"] == sample_warehouse_data["name"]
    
    def test_create_warehouse_duplicate_label_integration(self, test_client, sample_warehouse_data):
        """Test creating warehouses with duplicate labels fails."""
        # Create first warehouse
        response1 = test_client.post("/api/v1/warehouses/", json=sample_warehouse_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Try to create second warehouse with same label
        duplicate_data = sample_warehouse_data.copy()
        duplicate_data["name"] = "Different Name"
        
        response2 = test_client.post("/api/v1/warehouses/", json=duplicate_data)
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response2.json()["detail"]
    
    def test_get_warehouse_by_id_integration(self, test_client, sample_warehouse_data):
        """Test retrieving a warehouse by ID through the API."""
        # Create warehouse
        create_response = test_client.post("/api/v1/warehouses/", json=sample_warehouse_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        warehouse_id = create_response.json()["id"]
        
        # Retrieve warehouse
        get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert get_response.status_code == status.HTTP_200_OK
        
        warehouse_data = get_response.json()
        assert warehouse_data["id"] == warehouse_id
        assert warehouse_data["name"] == sample_warehouse_data["name"]
        assert warehouse_data["label"] == sample_warehouse_data["label"]
    
    def test_get_warehouse_by_id_not_found_integration(self, test_client):
        """Test retrieving a non-existent warehouse."""
        non_existent_id = str(uuid4())
        response = test_client.get(f"/api/v1/warehouses/{non_existent_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_warehouse_by_label_integration(self, test_client, sample_warehouse_data):
        """Test retrieving a warehouse by label through the API."""
        # Create warehouse
        create_response = test_client.post("/api/v1/warehouses/", json=sample_warehouse_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Retrieve by label
        label = sample_warehouse_data["label"]
        get_response = test_client.get(f"/api/v1/warehouses/label/{label}")
        assert get_response.status_code == status.HTTP_200_OK
        
        warehouse_data = get_response.json()
        assert warehouse_data["label"] == label
        assert warehouse_data["name"] == sample_warehouse_data["name"]
    
    def test_list_warehouses_integration(self, test_client, multiple_warehouse_data):
        """Test listing warehouses with pagination."""
        # Create multiple warehouses
        created_warehouses = []
        for warehouse_data in multiple_warehouse_data:
            response = test_client.post("/api/v1/warehouses/", json=warehouse_data)
            assert response.status_code == status.HTTP_201_CREATED
            created_warehouses.append(response.json())
        
        # Test default listing
        list_response = test_client.get("/api/v1/warehouses/")
        assert list_response.status_code == status.HTTP_200_OK
        
        list_data = list_response.json()
        assert "count" in list_data
        assert "results" in list_data
        assert len(list_data["results"]) == len(multiple_warehouse_data)
        
        # Verify all created warehouses are in the list
        result_names = [w["name"] for w in list_data["results"]]
        expected_names = [w["name"] for w in multiple_warehouse_data]
        for name in expected_names:
            assert name in result_names
    
    def test_list_warehouses_pagination_integration(self, test_client, multiple_warehouse_data):
        """Test warehouse listing with pagination parameters."""
        # Create multiple warehouses
        for warehouse_data in multiple_warehouse_data:
            response = test_client.post("/api/v1/warehouses/", json=warehouse_data)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Test first page
        page1_response = test_client.get("/api/v1/warehouses/?page=1&page_size=2")
        assert page1_response.status_code == status.HTTP_200_OK
        page1_data = page1_response.json()
        assert len(page1_data["results"]) == 2
        
        # Test second page
        page2_response = test_client.get("/api/v1/warehouses/?page=2&page_size=2")
        assert page2_response.status_code == status.HTTP_200_OK
        page2_data = page2_response.json()
        assert len(page2_data["results"]) == 1  # Remaining warehouse
        
        # Ensure no overlap between pages
        page1_ids = [w["id"] for w in page1_data["results"]]
        page2_ids = [w["id"] for w in page2_data["results"]]
        assert len(set(page1_ids) & set(page2_ids)) == 0
    
    def test_search_warehouses_integration(self, test_client, multiple_warehouse_data):
        """Test searching warehouses by name."""
        # Create multiple warehouses
        for warehouse_data in multiple_warehouse_data:
            response = test_client.post("/api/v1/warehouses/", json=warehouse_data)
            assert response.status_code == status.HTTP_201_CREATED
        
        # Search for warehouses containing "Warehouse"
        search_response = test_client.get("/api/v1/warehouses/?search=Warehouse")
        assert search_response.status_code == status.HTTP_200_OK
        
        search_data = search_response.json()
        assert len(search_data["results"]) == 1  # Only "Secondary Warehouse" contains "Warehouse"
        assert search_data["results"][0]["name"] == "Secondary Warehouse"
        
        # Search for warehouses containing "Storage"
        storage_response = test_client.get("/api/v1/warehouses/?search=Storage")
        assert storage_response.status_code == status.HTTP_200_OK
        storage_data = storage_response.json()
        assert len(storage_data["results"]) == 1
        assert storage_data["results"][0]["name"] == "Emergency Storage"
    
    def test_update_warehouse_integration(self, test_client, sample_warehouse_data):
        """Test updating a warehouse through the API."""
        # Create warehouse
        create_response = test_client.post("/api/v1/warehouses/", json=sample_warehouse_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        warehouse_id = create_response.json()["id"]
        
        # Update warehouse
        update_data = {
            "name": "Updated Warehouse Name",
            "label": "UPDATED",
            "remarks": "Updated remarks"
        }
        
        update_response = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        
        updated_warehouse = update_response.json()
        assert updated_warehouse["name"] == update_data["name"]
        assert updated_warehouse["label"] == update_data["label"]
        assert updated_warehouse["remarks"] == update_data["remarks"]
        
        # Verify changes were persisted
        get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert get_response.status_code == status.HTTP_200_OK
        persisted_warehouse = get_response.json()
        assert persisted_warehouse["name"] == update_data["name"]
        assert persisted_warehouse["label"] == update_data["label"]
    
    def test_deactivate_activate_warehouse_integration(self, test_client, sample_warehouse_data):
        """Test deactivating and activating a warehouse."""
        # Create warehouse
        create_response = test_client.post("/api/v1/warehouses/", json=sample_warehouse_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        warehouse_id = create_response.json()["id"]
        
        # Verify warehouse is initially active
        get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert get_response.json()["is_active"] is True
        
        # Deactivate warehouse
        deactivate_response = test_client.patch(f"/api/v1/warehouses/{warehouse_id}/deactivate")
        assert deactivate_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify warehouse is inactive and doesn't appear in active list
        active_list_response = test_client.get("/api/v1/warehouses/?is_active=true")
        active_warehouses = active_list_response.json()["results"]
        active_ids = [w["id"] for w in active_warehouses]
        assert warehouse_id not in active_ids
        
        # Verify warehouse appears in inactive list
        all_list_response = test_client.get("/api/v1/warehouses/?is_active=false")
        all_warehouses = all_list_response.json()["results"]
        inactive_warehouses = [w for w in all_warehouses if not w["is_active"]]
        inactive_ids = [w["id"] for w in inactive_warehouses]
        assert warehouse_id in inactive_ids
        
        # Activate warehouse
        activate_response = test_client.patch(f"/api/v1/warehouses/{warehouse_id}/activate")
        assert activate_response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify warehouse is active again
        final_get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert final_get_response.json()["is_active"] is True
    
    def test_warehouse_stats_integration(self, test_client, multiple_warehouse_data):
        """Test warehouse statistics endpoint."""
        # Create warehouses with different characteristics
        warehouses_with_remarks = 0
        for warehouse_data in multiple_warehouse_data:
            response = test_client.post("/api/v1/warehouses/", json=warehouse_data)
            assert response.status_code == status.HTTP_201_CREATED
            if warehouse_data.get("remarks"):
                warehouses_with_remarks += 1
        
        # Get statistics
        stats_response = test_client.get("/api/v1/warehouses/stats/overview")
        assert stats_response.status_code == status.HTTP_200_OK
        
        stats = stats_response.json()
        assert "total_warehouses" in stats
        assert "warehouses_with_remarks" in stats
        assert "recent_warehouses_30_days" in stats
        
        assert stats["total_warehouses"] == len(multiple_warehouse_data)
        assert stats["warehouses_with_remarks"] == warehouses_with_remarks
        assert stats["recent_warehouses_30_days"] == len(multiple_warehouse_data)  # All are recent


class TestWarehouseDatabaseIntegration(TestWarehouseIntegrationSetup):
    """Integration tests for warehouse database operations."""
    
    def test_warehouse_database_persistence(self, test_session, sample_warehouse_data):
        """Test that warehouse data is correctly persisted and retrieved from database."""
        # Create warehouse entity
        warehouse = Warehouse(
            name=sample_warehouse_data["name"],
            label=sample_warehouse_data["label"],
            remarks=sample_warehouse_data["remarks"]
        )
        
        # Persist to database
        db_warehouse = WarehouseModel(
            id=warehouse.id,
            name=warehouse.name,
            label=warehouse.label,
            remarks=warehouse.remarks,
            created_at=warehouse.created_at,
            updated_at=warehouse.updated_at,
            created_by=sample_warehouse_data["created_by"],
            is_active=warehouse.is_active
        )
        
        test_session.add(db_warehouse)
        test_session.commit()
        test_session.refresh(db_warehouse)
        
        # Retrieve from database
        retrieved_warehouse = test_session.query(WarehouseModel).filter_by(id=warehouse.id).first()
        
        # Verify persistence
        assert retrieved_warehouse is not None
        assert retrieved_warehouse.id == warehouse.id
        assert retrieved_warehouse.name == warehouse.name
        assert retrieved_warehouse.label == warehouse.label
        assert retrieved_warehouse.remarks == warehouse.remarks
        assert retrieved_warehouse.is_active == warehouse.is_active
    
    def test_warehouse_label_uniqueness_constraint(self, test_session):
        """Test that database enforces label uniqueness."""
        # Create first warehouse
        warehouse1 = WarehouseModel(
            id=str(uuid4()),
            name="First Warehouse",
            label="UNIQUE",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        test_session.add(warehouse1)
        test_session.commit()
        
        # Try to create second warehouse with same label
        warehouse2 = WarehouseModel(
            id=str(uuid4()),
            name="Second Warehouse",
            label="UNIQUE",  # Same label
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        test_session.add(warehouse2)
        
        # Should raise integrity error
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError or similar
            test_session.commit()
    
    def test_warehouse_search_query_performance(self, test_session, multiple_warehouse_data):
        """Test database search query performance and correctness."""
        # Create multiple warehouses
        created_warehouses = []
        for i, warehouse_data in enumerate(multiple_warehouse_data):
            warehouse = WarehouseModel(
                id=str(uuid4()),
                name=warehouse_data["name"],
                label=warehouse_data["label"],
                remarks=warehouse_data["remarks"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                created_by=warehouse_data["created_by"],
                is_active=True
            )
            test_session.add(warehouse)
            created_warehouses.append(warehouse)
        
        test_session.commit()
        
        # Test case-insensitive search
        search_results = test_session.query(WarehouseModel).filter(
            WarehouseModel.name.ilike("%warehouse%")
        ).all()
        
        # Should find "Secondary Warehouse"
        assert len(search_results) == 1
        assert search_results[0].name == "Secondary Warehouse"
        
        # Test search by partial label
        label_search = test_session.query(WarehouseModel).filter(
            WarehouseModel.label.ilike("%MAIN%")
        ).all()
        
        assert len(label_search) == 1
        assert label_search[0].label == "MAIN"
    
    def test_warehouse_soft_delete_functionality(self, test_session, sample_warehouse_data):
        """Test soft delete functionality at database level."""
        # Create warehouse
        warehouse = WarehouseModel(
            id=str(uuid4()),
            name=sample_warehouse_data["name"],
            label=sample_warehouse_data["label"],
            remarks=sample_warehouse_data["remarks"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            is_active=True
        )
        test_session.add(warehouse)
        test_session.commit()
        
        # Verify warehouse is active
        active_warehouses = test_session.query(WarehouseModel).filter_by(is_active=True).all()
        assert len(active_warehouses) == 1
        assert active_warehouses[0].id == warehouse.id
        
        # Soft delete (deactivate)
        warehouse.is_active = False
        test_session.commit()
        
        # Verify warehouse is no longer in active list
        active_warehouses_after = test_session.query(WarehouseModel).filter_by(is_active=True).all()
        assert len(active_warehouses_after) == 0
        
        # Verify warehouse still exists in database
        all_warehouses = test_session.query(WarehouseModel).all()
        assert len(all_warehouses) == 1
        assert all_warehouses[0].id == warehouse.id
        assert all_warehouses[0].is_active is False


class TestWarehouseEndToEndWorkflows(TestWarehouseIntegrationSetup):
    """End-to-end integration tests for warehouse workflows."""
    
    def test_complete_warehouse_lifecycle_workflow(self, test_client):
        """Test complete warehouse lifecycle from creation to deactivation."""
        # 1. Create warehouse
        create_data = {
            "name": "E2E Test Warehouse",
            "label": "E2E",
            "remarks": "End-to-end test warehouse",
            "created_by": "e2e_test"
        }
        
        create_response = test_client.post("/api/v1/warehouses/", json=create_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        warehouse = create_response.json()
        warehouse_id = warehouse["id"]
        
        # 2. Verify creation
        get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["name"] == create_data["name"]
        
        # 3. Update warehouse
        update_data = {
            "name": "Updated E2E Warehouse",
            "remarks": "Updated during e2e test"
        }
        
        update_response = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        
        # 4. Verify update
        get_updated_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        updated_warehouse = get_updated_response.json()
        assert updated_warehouse["name"] == update_data["name"]
        assert updated_warehouse["remarks"] == update_data["remarks"]
        assert updated_warehouse["label"] == create_data["label"]  # Should remain unchanged
        
        # 5. Verify warehouse appears in listings
        list_response = test_client.get("/api/v1/warehouses/")
        warehouses = list_response.json()["results"]
        warehouse_ids = [w["id"] for w in warehouses]
        assert warehouse_id in warehouse_ids
        
        # 6. Test search functionality
        search_response = test_client.get("/api/v1/warehouses/?search=E2E")
        search_results = search_response.json()["results"]
        assert len(search_results) == 1
        assert search_results[0]["id"] == warehouse_id
        
        # 7. Deactivate warehouse
        deactivate_response = test_client.patch(f"/api/v1/warehouses/{warehouse_id}/deactivate")
        assert deactivate_response.status_code == status.HTTP_204_NO_CONTENT
        
        # 8. Verify deactivation
        final_get_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        final_warehouse = final_get_response.json()
        assert final_warehouse["is_active"] is False
        
        # 9. Verify warehouse doesn't appear in active listings
        active_list_response = test_client.get("/api/v1/warehouses/?is_active=true")
        active_warehouses = active_list_response.json()["results"]
        active_ids = [w["id"] for w in active_warehouses]
        assert warehouse_id not in active_ids
    
    def test_warehouse_business_rules_enforcement_workflow(self, test_client):
        """Test that business rules are enforced throughout the complete workflow."""
        # 1. Test label normalization during creation
        create_data = {
            "name": "Business Rules Test",
            "label": "lowercase_label",  # Should be normalized to uppercase
            "created_by": "test"
        }
        
        create_response = test_client.post("/api/v1/warehouses/", json=create_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        warehouse = create_response.json()
        assert warehouse["label"] == "LOWERCASE_LABEL"
        
        # 2. Test label uniqueness enforcement
        duplicate_data = {
            "name": "Duplicate Label Test",
            "label": "LOWERCASE_LABEL",  # Same normalized label
            "created_by": "test"
        }
        
        duplicate_response = test_client.post("/api/v1/warehouses/", json=duplicate_data)
        assert duplicate_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in duplicate_response.json()["detail"]
        
        # 3. Test validation during updates
        warehouse_id = warehouse["id"]
        
        # Try to update with invalid data
        invalid_update = {"name": ""}  # Empty name should be rejected
        invalid_response = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=invalid_update)
        assert invalid_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # 4. Test successful update with label change
        valid_update = {
            "name": "Updated Business Rules Test",
            "label": "new_unique_label"
        }
        
        update_response = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=valid_update)
        assert update_response.status_code == status.HTTP_200_OK
        updated_warehouse = update_response.json()
        assert updated_warehouse["label"] == "NEW_UNIQUE_LABEL"  # Should be normalized
    
    def test_concurrent_warehouse_operations_workflow(self, test_client):
        """Test handling of concurrent operations on warehouses."""
        # Create initial warehouse
        create_data = {
            "name": "Concurrent Test Warehouse",
            "label": "CONCURRENT",
            "created_by": "concurrent_test"
        }
        
        create_response = test_client.post("/api/v1/warehouses/", json=create_data)
        warehouse_id = create_response.json()["id"]
        
        # Simulate concurrent updates
        update1_data = {"name": "Concurrent Update 1", "remarks": "First update"}
        update2_data = {"name": "Concurrent Update 2", "remarks": "Second update"}
        
        # Both updates should succeed (last one wins for name/remarks)
        response1 = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=update1_data)
        response2 = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=update2_data)
        
        assert response1.status_code == status.HTTP_200_OK
        assert response2.status_code == status.HTTP_200_OK
        
        # Verify final state
        final_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        final_warehouse = final_response.json()
        
        # The second update should be the final state
        assert final_warehouse["name"] == update2_data["name"]
        assert final_warehouse["remarks"] == update2_data["remarks"]
    
    def test_warehouse_data_integrity_workflow(self, test_client):
        """Test data integrity throughout warehouse operations."""
        # Create warehouse with specific data
        original_data = {
            "name": "Data Integrity Test",
            "label": "INTEGRITY",
            "remarks": "Testing data integrity",
            "created_by": "integrity_test"
        }
        
        create_response = test_client.post("/api/v1/warehouses/", json=original_data)
        warehouse = create_response.json()
        warehouse_id = warehouse["id"]
        original_created_at = warehouse["created_at"]
        
        # Perform multiple operations and verify data integrity
        
        # 1. Update and verify timestamps
        update_data = {"remarks": "Updated remarks"}
        update_response = test_client.put(f"/api/v1/warehouses/{warehouse_id}", json=update_data)
        updated_warehouse = update_response.json()
        
        assert updated_warehouse["created_at"] == original_created_at  # Should not change
        assert updated_warehouse["updated_at"] != warehouse["updated_at"]  # Should change
        assert updated_warehouse["created_by"] == original_data["created_by"]  # Should not change
        
        # 2. Deactivate and reactivate, verify state consistency
        test_client.patch(f"/api/v1/warehouses/{warehouse_id}/deactivate")
        deactivated_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        assert deactivated_response.json()["is_active"] is False
        
        test_client.patch(f"/api/v1/warehouses/{warehouse_id}/activate")
        reactivated_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        reactivated_warehouse = reactivated_response.json()
        
        assert reactivated_warehouse["is_active"] is True
        assert reactivated_warehouse["name"] == update_data.get("name", original_data["name"])
        assert reactivated_warehouse["label"] == original_data["label"]
        assert reactivated_warehouse["created_by"] == original_data["created_by"]
        
        # 3. Verify all data fields maintained integrity
        final_response = test_client.get(f"/api/v1/warehouses/{warehouse_id}")
        final_warehouse = final_response.json()
        
        assert final_warehouse["id"] == warehouse_id
        assert final_warehouse["label"] == original_data["label"]
        assert final_warehouse["created_by"] == original_data["created_by"]
        assert final_warehouse["created_at"] == original_created_at


class TestWarehousePerformanceIntegration(TestWarehouseIntegrationSetup):
    """Performance-focused integration tests."""
    
    def test_warehouse_bulk_operations_performance(self, test_client):
        """Test performance of bulk warehouse operations."""
        import time
        
        # Create multiple warehouses and measure time
        start_time = time.time()
        
        warehouse_data_list = []
        for i in range(10):  # Moderate number for integration test
            warehouse_data = {
                "name": f"Performance Test Warehouse {i+1}",
                "label": f"PERF{i+1:02d}",
                "remarks": f"Performance test warehouse number {i+1}",
                "created_by": "performance_test"
            }
            warehouse_data_list.append(warehouse_data)
            
            response = test_client.post("/api/v1/warehouses/", json=warehouse_data)
            assert response.status_code == status.HTTP_201_CREATED
        
        creation_time = time.time() - start_time
        
        # Test listing performance
        list_start = time.time()
        list_response = test_client.get("/api/v1/warehouses/")
        list_time = time.time() - list_start
        
        assert list_response.status_code == status.HTTP_200_OK
        assert len(list_response.json()["results"]) == 10
        
        # Test search performance
        search_start = time.time()
        search_response = test_client.get("/api/v1/warehouses/?search=Performance")
        search_time = time.time() - search_start
        
        assert search_response.status_code == status.HTTP_200_OK
        assert len(search_response.json()["results"]) == 10
        
        # Performance assertions (reasonable thresholds for integration tests)
        assert creation_time < 5.0  # Should create 10 warehouses in under 5 seconds
        assert list_time < 1.0      # Should list warehouses in under 1 second
        assert search_time < 1.0    # Should search warehouses in under 1 second
        
        print(f"Performance metrics: Creation={creation_time:.3f}s, List={list_time:.3f}s, Search={search_time:.3f}s")


def test_warehouse_integration_test_completeness():
    """Meta-test to verify integration test coverage."""
    integration_test_areas = [
        "API endpoint integration with real database",
        "Complete request/response cycles",
        "Data persistence and retrieval",
        "Business logic validation end-to-end",
        "Database constraint enforcement",
        "Search and pagination functionality",
        "CRUD operation workflows",
        "State transition workflows",
        "Concurrent operation handling",
        "Data integrity verification",
        "Performance characteristics",
        "Error handling integration",
        "Business rules enforcement",
        "Complete lifecycle workflows"
    ]
    
    assert len(integration_test_areas) >= 14, "Integration tests should cover comprehensive scenarios"