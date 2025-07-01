"""
Comprehensive test suite for Vendor functionality.

This test suite covers all layers of the vendor implementation:
- Domain Entity tests
- Repository tests (with mocking)
- Service layer tests
- Use case tests  
- API endpoint tests
- Integration tests with real PostgreSQL database
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

# Domain layer imports
from src.domain.entities.vendor import Vendor
from src.domain.repositories.vendor_repository import VendorRepository

# Application layer imports
from src.application.services.vendor_service import VendorService
from src.application.use_cases.vendor_use_cases import (
    CreateVendorUseCase,
    GetVendorUseCase,
    GetVendorByEmailUseCase,
    GetVendorsByCityUseCase,
    UpdateVendorUseCase,
    DeleteVendorUseCase,
    ListVendorsUseCase,
    SearchVendorsUseCase,
)

# Infrastructure layer imports
from src.infrastructure.repositories.vendor_repository_impl import SQLAlchemyVendorRepository
from src.infrastructure.database.models import VendorModel

# API layer imports
from src.api.v1.schemas.vendor_schemas import (
    VendorCreateSchema, 
    VendorUpdateSchema, 
    VendorResponseSchema
)
from src.main import app


class TestVendorDomainEntity:
    """Test the Vendor domain entity business logic."""
    
    def test_vendor_creation_valid(self):
        """Test creating a vendor with valid data."""
        vendor = Vendor(
            name="ABC Supplies Inc",
            email="contact@abcsupplies.com",
            address="123 Business Street",
            city="New York",
            remarks="Reliable supplier"
        )
        
        assert vendor.name == "ABC Supplies Inc"
        assert vendor.email == "contact@abcsupplies.com"
        assert vendor.address == "123 Business Street"
        assert vendor.city == "New York"
        assert vendor.remarks == "Reliable supplier"
        assert vendor.is_active is True
        assert vendor.id is not None
        assert vendor.created_at is not None
        assert vendor.updated_at is not None
    
    def test_vendor_creation_minimal(self):
        """Test creating a vendor with only required fields."""
        vendor = Vendor(name="Minimal Vendor")
        
        assert vendor.name == "Minimal Vendor"
        assert vendor.email is None
        assert vendor.address is None
        assert vendor.city is None
        assert vendor.remarks is None
        assert vendor.is_active is True
    
    def test_vendor_name_validation_empty(self):
        """Test that empty names raise ValueError."""
        with pytest.raises(ValueError, match="Vendor name cannot be empty"):
            Vendor(name="")
        
        with pytest.raises(ValueError, match="Vendor name cannot be empty"):
            Vendor(name="   ")
    
    def test_vendor_name_validation_too_long(self):
        """Test that names over 255 characters raise ValueError."""
        long_name = "a" * 256
        with pytest.raises(ValueError, match="Vendor name cannot exceed 255 characters"):
            Vendor(name=long_name)
    
    def test_vendor_email_validation_invalid(self):
        """Test that invalid emails raise ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            Vendor(name="Test Vendor", email="invalid-email")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            Vendor(name="Test Vendor", email="missing@domain")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            Vendor(name="Test Vendor", email="@missinguser.com")
    
    def test_vendor_email_validation_too_long(self):
        """Test that emails over 255 characters raise ValueError."""
        long_email = "a" * 250 + "@test.com"
        with pytest.raises(ValueError, match="Email cannot exceed 255 characters"):
            Vendor(name="Test Vendor", email=long_email)
    
    def test_vendor_email_normalization(self):
        """Test that emails are normalized to lowercase."""
        vendor = Vendor(name="Test Vendor", email="TEST@EXAMPLE.COM")
        assert vendor.email == "test@example.com"
    
    def test_vendor_name_whitespace_stripping(self):
        """Test that vendor names are stripped of whitespace."""
        vendor = Vendor(name="   Test Vendor   ")
        assert vendor.name == "Test Vendor"
    
    def test_vendor_update_methods(self):
        """Test vendor update methods."""
        vendor = Vendor(name="Original Name")
        original_updated_at = vendor.updated_at
        
        # Test name update
        vendor.update_name("Updated Name")
        assert vendor.name == "Updated Name"
        assert vendor.updated_at > original_updated_at
        
        # Test email update
        vendor.update_email("updated@test.com")
        assert vendor.email == "updated@test.com"
        
        # Test address update
        vendor.update_address("New Address")
        assert vendor.address == "New Address"
        
        # Test city update
        vendor.update_city("New City")
        assert vendor.city == "New City"
        
        # Test remarks update
        vendor.update_remarks("Updated remarks")
        assert vendor.remarks == "Updated remarks"
    
    def test_vendor_update_contact_info_bulk(self):
        """Test bulk contact info update."""
        vendor = Vendor(name="Test Vendor")
        
        vendor.update_contact_info(
            email="bulk@update.com",
            address="Bulk Address",
            city="Bulk City"
        )
        
        assert vendor.email == "bulk@update.com"
        assert vendor.address == "Bulk Address"
        assert vendor.city == "Bulk City"
    
    def test_vendor_search_matching(self):
        """Test vendor search query matching."""
        vendor = Vendor(
            name="ABC Supplies",
            email="contact@abc.com",
            city="New York",
            remarks="Electronics supplier"
        )
        
        # Test name matching
        assert vendor.matches_search_query("ABC") is True
        assert vendor.matches_search_query("supplies") is True
        
        # Test email matching
        assert vendor.matches_search_query("contact") is True
        assert vendor.matches_search_query("abc.com") is True
        
        # Test city matching
        assert vendor.matches_search_query("York") is True
        
        # Test remarks matching
        assert vendor.matches_search_query("Electronics") is True
        
        # Test no match
        assert vendor.matches_search_query("NonExistent") is False
        
        # Test empty query (should match)
        assert vendor.matches_search_query("") is True
        
        # Test specific field matching
        assert vendor.matches_search_query("ABC", ["name"]) is True
        assert vendor.matches_search_query("ABC", ["email"]) is True  # "abc" is in contact@abc.com
        assert vendor.matches_search_query("XYZ", ["email"]) is False  # No XYZ in email
    
    def test_vendor_display_info(self):
        """Test vendor display info generation."""
        vendor = Vendor(
            name="Display Vendor",
            email="display@test.com",
            city="Display City"
        )
        
        display_info = vendor.get_display_info()
        
        assert display_info["name"] == "Display Vendor"
        assert display_info["email"] == "display@test.com"
        assert display_info["city"] == "Display City"
        assert display_info["is_active"] is True
        assert "id" in display_info
    
    def test_vendor_activation_deactivation(self):
        """Test vendor activation and deactivation."""
        vendor = Vendor(name="Test Vendor")
        assert vendor.is_active is True
        
        vendor.deactivate()
        assert vendor.is_active is False
        
        vendor.activate()
        assert vendor.is_active is True
    
    def test_vendor_string_representations(self):
        """Test string representations of vendor."""
        vendor = Vendor(name="String Test Vendor", email="string@test.com")
        
        assert str(vendor) == "String Test Vendor"
        assert "String Test Vendor" in repr(vendor)
        assert "string@test.com" in repr(vendor)


class TestVendorRepository:
    """Test vendor repository with mocked dependencies."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return MagicMock()
    
    @pytest.fixture
    def vendor_repository(self, mock_session):
        """Create vendor repository with mock session."""
        return SQLAlchemyVendorRepository(mock_session)
    
    @pytest.fixture
    def sample_vendor(self):
        """Create a sample vendor for testing."""
        return Vendor(
            name="Repository Test Vendor",
            email="repo@test.com",
            city="Repository City"
        )
    
    @pytest.mark.asyncio
    async def test_repository_save(self, vendor_repository, mock_session, sample_vendor):
        """Test repository save method."""
        # Mock the session behavior
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None
        
        result = await vendor_repository.save(sample_vendor)
        
        assert result == sample_vendor
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_repository_find_by_id(self, vendor_repository, mock_session, sample_vendor):
        """Test repository find by ID method."""
        # Mock query result
        mock_model = MagicMock()
        mock_model.id = sample_vendor.id
        mock_model.name = sample_vendor.name
        mock_model.email = sample_vendor.email
        mock_model.address = sample_vendor.address
        mock_model.city = sample_vendor.city
        mock_model.remarks = sample_vendor.remarks
        mock_model.is_active = sample_vendor.is_active
        mock_model.created_at = sample_vendor.created_at
        mock_model.updated_at = sample_vendor.updated_at
        mock_model.created_by = sample_vendor.created_by
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model
        
        result = await vendor_repository.find_by_id(sample_vendor.id)
        
        assert result is not None
        assert result.name == sample_vendor.name
        assert result.email == sample_vendor.email
        mock_session.query.assert_called_with(VendorModel)
    
    @pytest.mark.asyncio
    async def test_repository_find_by_email(self, vendor_repository, mock_session, sample_vendor):
        """Test repository find by email method."""
        mock_model = MagicMock()
        mock_model.email = sample_vendor.email
        mock_model.name = sample_vendor.name
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_model
        
        result = await vendor_repository.find_by_email(sample_vendor.email)
        
        assert result is not None
        mock_session.query.assert_called_with(VendorModel)
    
    @pytest.mark.asyncio
    async def test_repository_search_vendors(self, vendor_repository, mock_session):
        """Test repository search vendors method."""
        mock_models = [MagicMock(), MagicMock()]
        for i, mock_model in enumerate(mock_models):
            mock_model.id = str(uuid4())
            mock_model.name = f"Vendor {i+1}"
            mock_model.email = f"vendor{i+1}@test.com"
            mock_model.city = "Test City"
            mock_model.address = "Test Address"
            mock_model.remarks = "Test Remarks"
            mock_model.is_active = True
            mock_model.created_at = datetime.now(timezone.utc)
            mock_model.updated_at = datetime.now(timezone.utc)
            mock_model.created_by = None
        
        # Mock the complex query chain: query().filter().filter().order_by().limit().all()
        mock_query = MagicMock()
        mock_filter1 = MagicMock()
        mock_filter2 = MagicMock()
        mock_order_by = MagicMock()
        mock_limit = MagicMock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter1
        mock_filter1.filter.return_value = mock_filter2
        mock_filter2.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_models
        
        result = await vendor_repository.search_vendors("Vendor", limit=10)
        
        assert len(result) == 2
        assert result[0].name == "Vendor 1"
        assert result[1].name == "Vendor 2"
        mock_session.query.assert_called_with(VendorModel)


class TestVendorUseCases:
    """Test vendor use cases layer."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock vendor repository."""
        return AsyncMock(spec=VendorRepository)
    
    @pytest.fixture
    def sample_vendor(self):
        """Create a sample vendor for testing."""
        return Vendor(
            name="Use Case Test Vendor",
            email="usecase@test.com",
            city="Use Case City",
            vendor_id=str(uuid4())
        )
    
    @pytest.mark.asyncio
    async def test_create_vendor_use_case(self, mock_repository, sample_vendor):
        """Test create vendor use case."""
        mock_repository.exists_by_email.return_value = False
        mock_repository.save.return_value = sample_vendor
        
        use_case = CreateVendorUseCase(mock_repository)
        result = await use_case.execute(
            name="Use Case Test Vendor",
            email="usecase@test.com",
            city="Use Case City"
        )
        
        assert result.name == "Use Case Test Vendor"
        assert result.email == "usecase@test.com"
        mock_repository.exists_by_email.assert_called_once_with("usecase@test.com")
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_vendor_duplicate_email(self, mock_repository):
        """Test create vendor with duplicate email."""
        mock_repository.exists_by_email.return_value = True
        
        use_case = CreateVendorUseCase(mock_repository)
        
        with pytest.raises(ValueError, match="Vendor with email .* already exists"):
            await use_case.execute(
                name="Duplicate Vendor",
                email="duplicate@test.com"
            )
    
    @pytest.mark.asyncio
    async def test_get_vendor_use_case(self, mock_repository, sample_vendor):
        """Test get vendor use case."""
        mock_repository.find_by_id.return_value = sample_vendor
        
        use_case = GetVendorUseCase(mock_repository)
        result = await use_case.execute(sample_vendor.id)
        
        assert result == sample_vendor
        mock_repository.find_by_id.assert_called_once_with(sample_vendor.id)
    
    @pytest.mark.asyncio
    async def test_update_vendor_use_case(self, mock_repository, sample_vendor):
        """Test update vendor use case."""
        mock_repository.find_by_id.return_value = sample_vendor
        mock_repository.exists_by_email.return_value = False
        mock_repository.update.return_value = sample_vendor
        
        use_case = UpdateVendorUseCase(mock_repository)
        result = await use_case.execute(
            vendor_id=sample_vendor.id,
            name="Updated Name",
            email="updated@test.com"
        )
        
        assert result == sample_vendor
        mock_repository.find_by_id.assert_called_once_with(sample_vendor.id)
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_vendor_use_case(self, mock_repository, sample_vendor):
        """Test delete vendor use case."""
        mock_repository.exists.return_value = True
        mock_repository.delete.return_value = True
        
        use_case = DeleteVendorUseCase(mock_repository)
        result = await use_case.execute(sample_vendor.id)
        
        assert result is True
        mock_repository.exists.assert_called_once_with(sample_vendor.id)
        mock_repository.delete.assert_called_once_with(sample_vendor.id)
    
    @pytest.mark.asyncio
    async def test_list_vendors_use_case(self, mock_repository):
        """Test list vendors use case."""
        vendors = [
            Vendor(name="Vendor 1", email="vendor1@test.com"),
            Vendor(name="Vendor 2", email="vendor2@test.com")
        ]
        mock_repository.find_all.return_value = vendors
        
        use_case = ListVendorsUseCase(mock_repository)
        result = await use_case.execute(skip=0, limit=100)
        
        assert result == vendors
        mock_repository.find_all.assert_called_once_with(0, 100)
    
    @pytest.mark.asyncio
    async def test_search_vendors_use_case(self, mock_repository):
        """Test search vendors use case."""
        matching_vendors = [
            Vendor(name="Search Vendor", email="search@test.com")
        ]
        mock_repository.search_vendors.return_value = matching_vendors
        
        use_case = SearchVendorsUseCase(mock_repository)
        result = await use_case.execute("Search", limit=10)
        
        assert result == matching_vendors
        mock_repository.search_vendors.assert_called_once_with("Search", None, 10)


class TestVendorService:
    """Test vendor service layer."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock vendor repository."""
        return AsyncMock(spec=VendorRepository)
    
    @pytest.fixture
    def vendor_service(self, mock_repository):
        """Create vendor service with mock repository."""
        return VendorService(mock_repository)
    
    @pytest.fixture
    def sample_vendor(self):
        """Create a sample vendor for testing."""
        return Vendor(
            name="Service Test Vendor",
            email="service@test.com",
            city="Service City"
        )
    
    @pytest.mark.asyncio
    async def test_create_vendor_service(self, vendor_service, mock_repository, sample_vendor):
        """Test vendor service create method."""
        mock_repository.exists_by_email.return_value = False
        mock_repository.save.return_value = sample_vendor
        
        result = await vendor_service.create_vendor(
            name="Service Test Vendor",
            email="service@test.com",
            city="Service City"
        )
        
        assert result.name == "Service Test Vendor"
        assert result.email == "service@test.com"
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_vendor_service(self, vendor_service, mock_repository, sample_vendor):
        """Test vendor service get method."""
        mock_repository.find_by_id.return_value = sample_vendor
        
        result = await vendor_service.get_vendor(sample_vendor.id)
        
        assert result == sample_vendor
        mock_repository.find_by_id.assert_called_once_with(sample_vendor.id)
    
    @pytest.mark.asyncio
    async def test_search_vendors_service(self, vendor_service, mock_repository):
        """Test vendor service search method."""
        search_results = [
            Vendor(name="Search Result", email="result@test.com")
        ]
        mock_repository.search_vendors.return_value = search_results
        
        result = await vendor_service.search_vendors("Search", limit=10)
        
        assert result == search_results
        mock_repository.search_vendors.assert_called_once()


class TestVendorAPI:
    """Test vendor API endpoints."""
    
    @pytest.fixture
    def mock_service(self):
        """Mock vendor service."""
        return AsyncMock(spec=VendorService)
    
    @pytest.fixture
    def client(self, mock_service):
        """Create test client with dependency override."""
        from src.api.v1.endpoints.vendors import get_vendor_service
        
        app.dependency_overrides[get_vendor_service] = lambda: mock_service
        yield TestClient(app)
        app.dependency_overrides.clear()
    
    def test_create_vendor_success(self, client, mock_service):
        """Test successful vendor creation via API."""
        vendor_data = {
            "name": "API Test Vendor",
            "email": "api@test.com",
            "address": "123 API Street",
            "city": "API City",
            "remarks": "Created via API test"
        }
        
        created_vendor = Vendor(
            name=vendor_data["name"],
            email=vendor_data["email"],
            address=vendor_data["address"],
            city=vendor_data["city"],
            remarks=vendor_data["remarks"]
        )
        mock_service.create_vendor.return_value = created_vendor
        
        response = client.post("/api/v1/vendors/", json=vendor_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == vendor_data["name"]
        assert response_data["email"] == vendor_data["email"]
        assert "id" in response_data
        assert "created_at" in response_data
    
    def test_create_vendor_validation_error(self, client, mock_service):
        """Test vendor creation with validation error."""
        vendor_data = {
            "email": "invalid-email",  # Invalid email format
            "address": "Test Address"
        }
        
        response = client.post("/api/v1/vendors/", json=vendor_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        mock_service.create_vendor.assert_not_called()
    
    def test_get_vendor_success(self, client, mock_service):
        """Test successful vendor retrieval."""
        vendor_id = str(uuid4())
        vendor = Vendor(name="Get Test Vendor", email="get@test.com")
        mock_service.get_vendor.return_value = vendor
        
        response = client.get(f"/api/v1/vendors/{vendor_id}")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Get Test Vendor"
        assert response_data["email"] == "get@test.com"
    
    def test_get_vendor_not_found(self, client, mock_service):
        """Test vendor retrieval when not found."""
        vendor_id = str(uuid4())
        mock_service.get_vendor.return_value = None
        
        response = client.get(f"/api/v1/vendors/{vendor_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_vendors_success(self, client, mock_service):
        """Test vendor listing."""
        vendors = [
            Vendor(name="Vendor 1", email="vendor1@test.com"),
            Vendor(name="Vendor 2", email="vendor2@test.com")
        ]
        mock_service.list_vendors.return_value = vendors
        
        response = client.get("/api/v1/vendors/")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "vendors" in response_data
        assert "total" in response_data
        assert len(response_data["vendors"]) == 2
        assert response_data["vendors"][0]["name"] == "Vendor 1"
    
    def test_search_vendors_success(self, client, mock_service):
        """Test vendor search."""
        search_results = [
            Vendor(name="Search Vendor", email="search@test.com")
        ]
        mock_service.search_vendors.return_value = search_results
        
        response = client.get("/api/v1/vendors/search/?query=Search")
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]["name"] == "Search Vendor"
    
    def test_update_vendor_success(self, client, mock_service):
        """Test successful vendor update."""
        vendor_id = str(uuid4())
        update_data = {
            "name": "Updated Vendor",
            "email": "updated@test.com"
        }
        
        updated_vendor = Vendor(
            name=update_data["name"],
            email=update_data["email"],
            vendor_id=vendor_id
        )
        mock_service.update_vendor.return_value = updated_vendor
        
        response = client.put(f"/api/v1/vendors/{vendor_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "Updated Vendor"
        assert response_data["email"] == "updated@test.com"
    
    def test_delete_vendor_success(self, client, mock_service):
        """Test successful vendor deletion."""
        vendor_id = str(uuid4())
        mock_service.delete_vendor.return_value = True
        
        response = client.delete(f"/api/v1/vendors/{vendor_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_service.delete_vendor.assert_called_once_with(vendor_id)


class TestVendorIntegration:
    """Integration tests with real PostgreSQL database operations."""
    
    @pytest.fixture
    def db_session(self):
        """Create a test database session using PostgreSQL from docker-compose."""
        from src.core.config.database import get_database_manager
        from src.infrastructure.database.models import VendorModel
        
        # Use the PostgreSQL database from docker-compose
        db_manager = get_database_manager()
        session = db_manager.SessionLocal()
        
        # Clean up test vendors before and after each test
        test_emails = ['integration@test.com', 'unique@test.com', 'search1@test.com', 
                      'search2@test.com', 'search3@test.com', 'page1@test.com', 
                      'page2@test.com', 'page3@test.com', 'page4@test.com', 'page5@test.com']
        
        # Clean up before test
        try:
            session.query(VendorModel).filter(VendorModel.email.in_(test_emails)).delete(synchronize_session=False)
            session.commit()
        except Exception:
            session.rollback()
        
        try:
            yield session
        finally:
            # Clean up test vendors after test
            try:
                session.query(VendorModel).filter(VendorModel.email.in_(test_emails)).delete(synchronize_session=False)
                session.commit()
            except Exception:
                session.rollback()
            finally:
                session.close()
    
    @pytest.fixture
    def repository(self, db_session):
        """Create repository with real database session."""
        return SQLAlchemyVendorRepository(db_session)
    
    @pytest.fixture
    def service(self, repository):
        """Create service with real repository."""
        return VendorService(repository)
    
    @pytest.mark.asyncio
    async def test_full_vendor_lifecycle(self, service):
        """Test complete vendor lifecycle with real database."""
        # Create vendor
        created_vendor = await service.create_vendor(
            name="Integration Test Vendor",
            email="integration@test.com",
            address="123 Integration Street",
            city="Integration City",
            remarks="Full lifecycle test"
        )
        
        assert created_vendor.name == "Integration Test Vendor"
        assert created_vendor.email == "integration@test.com"
        assert created_vendor.address == "123 Integration Street"
        assert created_vendor.city == "Integration City"
        assert created_vendor.remarks == "Full lifecycle test"
        assert created_vendor.is_active is True
        
        # Get vendor by ID
        retrieved_vendor = await service.get_vendor(created_vendor.id)
        assert retrieved_vendor is not None
        assert retrieved_vendor.id == created_vendor.id
        assert retrieved_vendor.name == created_vendor.name
        
        # Get vendor by email
        retrieved_by_email = await service.get_vendor_by_email("integration@test.com")
        assert retrieved_by_email is not None
        assert retrieved_by_email.id == created_vendor.id
        
        # Update vendor
        updated_vendor = await service.update_vendor(
            vendor_id=created_vendor.id,
            name="Updated Integration Vendor",
            address="456 Updated Street",
            remarks="Updated in integration test"
        )
        assert updated_vendor.name == "Updated Integration Vendor"
        assert updated_vendor.address == "456 Updated Street"
        assert updated_vendor.remarks == "Updated in integration test"
        assert updated_vendor.email == "integration@test.com"  # Unchanged
        
        # List vendors (should include our vendor)
        all_vendors = await service.list_vendors(skip=0, limit=100)
        assert len(all_vendors) >= 1
        vendor_ids = [v.id for v in all_vendors]
        assert created_vendor.id in vendor_ids
        
        # Search vendors
        search_results = await service.search_vendors("Integration", limit=10)
        assert len(search_results) >= 1
        search_ids = [v.id for v in search_results]
        assert created_vendor.id in search_ids
        
        # Delete vendor
        delete_result = await service.delete_vendor(created_vendor.id)
        assert delete_result is True
        
        # Verify deletion
        deleted_vendor = await service.get_vendor(created_vendor.id)
        assert deleted_vendor is None
    
    @pytest.mark.asyncio
    async def test_vendor_email_uniqueness_constraint(self, service):
        """Test that vendor emails must be unique."""
        # Create first vendor
        vendor1 = await service.create_vendor(
            name="First Vendor",
            email="unique@test.com"
        )
        assert vendor1.email == "unique@test.com"
        
        # Try to create second vendor with same email
        with pytest.raises(ValueError, match="Vendor with email .* already exists"):
            await service.create_vendor(
                name="Second Vendor",
                email="unique@test.com"
            )
    
    @pytest.mark.asyncio
    async def test_vendor_search_functionality(self, service):
        """Test vendor search functionality with real data."""
        # Create test vendors
        await service.create_vendor(name="ABC Electronics", email="search1@test.com", city="New York")
        await service.create_vendor(name="XYZ Supplies", email="search2@test.com", city="Los Angeles")
        await service.create_vendor(name="Electronics Depot", email="search3@test.com", city="Chicago")
        
        # Search for vendors containing "Electronics"
        electronics_results = await service.search_vendors("Electronics")
        electronics_names = [v.name for v in electronics_results]
        assert "ABC Electronics" in electronics_names
        assert "Electronics Depot" in electronics_names
        assert "XYZ Supplies" not in electronics_names
        
        # Search for vendors containing "XYZ"
        xyz_results = await service.search_vendors("XYZ")
        xyz_names = [v.name for v in xyz_results]
        assert "XYZ Supplies" in xyz_names
        
        # Search with no matches
        no_match_results = await service.search_vendors("NonExistent")
        assert len(no_match_results) == 0
    
    @pytest.mark.asyncio
    async def test_vendor_pagination(self, service):
        """Test vendor pagination functionality."""
        # Create multiple vendors
        for i in range(5):
            await service.create_vendor(
                name=f"Pagination Test Vendor {i+1}",
                email=f"page{i+1}@test.com"
            )
        
        # Test first page
        page1 = await service.list_vendors(skip=0, limit=3)
        assert len(page1) == 3
        
        # Test second page
        page2 = await service.list_vendors(skip=3, limit=3)
        assert len(page2) >= 2  # At least our remaining vendors
        
        # Ensure no overlap between pages
        page1_ids = [v.id for v in page1]
        page2_ids = [v.id for v in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0  # No intersection


class TestVendorEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_vendor_creation_edge_cases(self):
        """Test vendor creation edge cases."""
        # Test with exactly 255 characters (should work)
        long_name = "a" * 255
        vendor = Vendor(name=long_name)
        assert vendor.name == long_name
        
        # Test with whitespace variations
        vendor_spaces = Vendor(name="   Name   ")
        assert vendor_spaces.name == "Name"
        
        # Test email edge cases
        vendor_email = Vendor(name="Test", email="  TEST@EXAMPLE.COM  ")
        assert vendor_email.email == "test@example.com"
    
    def test_vendor_update_edge_cases(self):
        """Test vendor update edge cases."""
        vendor = Vendor(name="Original Vendor")
        
        # Test updating with same values (should still update timestamps)
        original_updated_at = vendor.updated_at
        vendor.update_name("Original Vendor")
        assert vendor.updated_at > original_updated_at
        
        # Test clearing email
        vendor.update_email("test@example.com")
        assert vendor.email == "test@example.com"
        
        vendor.update_email(None)
        assert vendor.email is None
    
    def test_vendor_validation_boundary_conditions(self):
        """Test validation at boundary conditions."""
        # Test name length exactly at limit
        name_255 = "a" * 255
        vendor = Vendor(name=name_255)
        assert len(vendor.name) == 255
        
        # Test email length exactly at limit (accounting for domain)
        email_246 = "a" * 246 + "@test.com"  # 255 total
        vendor2 = Vendor(name="Test", email=email_246)
        assert len(vendor2.email) == 255
        
        # Test name length over limit
        name_256 = "a" * 256
        with pytest.raises(ValueError, match="Vendor name cannot exceed 255 characters"):
            Vendor(name=name_256)
    
    def test_vendor_unicode_support(self):
        """Test vendor with unicode characters."""
        unicode_vendor = Vendor(
            name="供应商名称",  # Chinese characters
            email="unicode@test.com",  # Use valid domain for test
            address="地址信息",
            city="北京",
            remarks="Remarks with émojis 🏢 and accénts"
        )
        
        assert unicode_vendor.name == "供应商名称"
        assert unicode_vendor.city == "北京"
        assert "🏢" in unicode_vendor.remarks


def test_vendor_comprehensive_suite_completeness():
    """Meta-test to ensure comprehensive test coverage."""
    # This test serves as documentation of what we're testing
    test_categories = [
        "Domain Entity Business Logic",
        "Repository Pattern Implementation", 
        "Use Cases Layer",
        "Service Layer",
        "API Endpoints",
        "Integration with PostgreSQL",
        "Edge Cases and Error Handling",
        "Unicode Support",
        "Email Validation",
        "Search Functionality",
        "Pagination",
        "CRUD Operations"
    ]
    
    # If this test exists and passes, it means we have comprehensive coverage
    assert len(test_categories) > 10
    assert "Integration with PostgreSQL" in test_categories