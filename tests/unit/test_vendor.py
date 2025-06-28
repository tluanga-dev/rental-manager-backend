import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from src.domain.entities.vendor import Vendor
from src.application.use_cases.vendor_use_cases import (
    CreateVendorUseCase,
    GetVendorUseCase,
    UpdateVendorUseCase,
    DeleteVendorUseCase,
    ListVendorsUseCase,
    SearchVendorsUseCase
)
from src.application.services.vendor_service import VendorService


@pytest.mark.unit
class TestVendorEntity:
    """Test Vendor domain entity"""

    def test_create_vendor_with_valid_data(self, sample_vendor_data):
        """Test creating vendor with valid data"""
        vendor = Vendor(
            name=sample_vendor_data["name"],
            email=sample_vendor_data["email"],
            address=sample_vendor_data["address"],
            city=sample_vendor_data["city"],
            remarks=sample_vendor_data["remarks"]
        )
        
        assert vendor.name == sample_vendor_data["name"]
        assert vendor.email == sample_vendor_data["email"].lower()
        assert vendor.city == sample_vendor_data["city"].title()
        assert vendor.is_active is True

    def test_email_normalization(self):
        """Test that email is normalized to lowercase"""
        vendor = Vendor(
            name="Test Vendor",
            email="TEST.VENDOR@EXAMPLE.COM",
            city="test city"
        )
        
        assert vendor.email == "test.vendor@example.com"
        assert vendor.city == "test city"

    def test_invalid_email_format(self):
        """Test that invalid email format raises error"""
        with pytest.raises(ValueError, match="Invalid email format"):
            Vendor(
                name="Test Vendor",
                email="invalid-email"
            )

    def test_empty_name_validation(self):
        """Test that empty name raises error"""
        with pytest.raises(ValueError, match="Vendor name cannot be empty"):
            Vendor(
                name="",
                email="test@example.com"
            )

    def test_update_email(self, sample_vendor):
        """Test updating vendor email"""
        new_email = "NEW.EMAIL@VENDOR.COM"
        original_updated_at = sample_vendor.updated_at
        
        sample_vendor.update_email(new_email)
        
        assert sample_vendor.email == "new.email@vendor.com"
        assert sample_vendor.updated_at > original_updated_at

    def test_deactivate_vendor(self, sample_vendor):
        """Test deactivating vendor"""
        sample_vendor.deactivate()
        
        assert sample_vendor.is_active is False

    def test_activate_vendor(self, sample_vendor):
        """Test activating vendor"""
        sample_vendor.deactivate()
        sample_vendor.activate()
        
        assert sample_vendor.is_active is True


@pytest.mark.unit
class TestVendorUseCases:
    """Test Vendor use cases"""

    @pytest.mark.asyncio
    async def test_create_vendor_use_case(self, sample_vendor_data):
        """Test creating vendor through use case"""
        mock_repository = Mock()
        mock_repository.exists_by_email = AsyncMock(return_value=False)
        mock_repository.save = AsyncMock(return_value=Vendor(
            name=sample_vendor_data["name"],
            email=sample_vendor_data["email"],
            address=sample_vendor_data["address"],
            city=sample_vendor_data["city"]
        ))
        
        use_case = CreateVendorUseCase(mock_repository)
        result = await use_case.execute(
            name=sample_vendor_data["name"],
            email=sample_vendor_data["email"],
            address=sample_vendor_data["address"],
            city=sample_vendor_data["city"]
        )
        
        assert result.name == sample_vendor_data["name"]
        mock_repository.exists_by_email.assert_called_once()
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_vendor_duplicate_email(self, sample_vendor_data):
        """Test creating vendor with duplicate email raises error"""
        mock_repository = Mock()
        mock_repository.exists_by_email = AsyncMock(return_value=True)
        
        use_case = CreateVendorUseCase(mock_repository)
        
        with pytest.raises(ValueError, match="already exists"):
            await use_case.execute(
                name=sample_vendor_data["name"],
                email=sample_vendor_data["email"]
            )

    @pytest.mark.asyncio
    async def test_get_vendor_use_case(self, sample_vendor):
        """Test getting vendor by ID"""
        vendor_id = uuid4()
        mock_repository = Mock()
        mock_repository.find_by_id = AsyncMock(return_value=sample_vendor)
        
        use_case = GetVendorUseCase(mock_repository)
        result = await use_case.execute(vendor_id)
        
        assert result == sample_vendor
        mock_repository.find_by_id.assert_called_once_with(vendor_id)

    @pytest.mark.asyncio
    async def test_update_vendor_use_case(self, sample_vendor):
        """Test updating vendor"""
        vendor_id = uuid4()
        new_name = "Updated Vendor Name"
        
        mock_repository = Mock()
        mock_repository.find_by_id = AsyncMock(return_value=sample_vendor)
        mock_repository.update = AsyncMock(return_value=sample_vendor)
        
        use_case = UpdateVendorUseCase(mock_repository)
        result = await use_case.execute(vendor_id, name=new_name)
        
        assert result == sample_vendor
        mock_repository.find_by_id.assert_called_once_with(vendor_id)
        mock_repository.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_vendor_use_case(self, mock_vendor_repository):
        """Test deleting vendor"""
        vendor_id = uuid4()
        mock_vendor_repository.exists.return_value = True
        mock_vendor_repository.delete.return_value = True
        
        use_case = DeleteVendorUseCase(mock_vendor_repository)
        result = await use_case.execute(vendor_id)
        
        assert result is True
        mock_vendor_repository.delete.assert_called_once_with(vendor_id)

    @pytest.mark.asyncio
    async def test_list_vendors_use_case(self, sample_vendor):
        """Test listing vendors"""
        mock_repository = Mock()
        mock_repository.find_all = AsyncMock(return_value=[sample_vendor])
        
        use_case = ListVendorsUseCase(mock_repository)
        result = await use_case.execute(skip=0, limit=10)
        
        assert result == [sample_vendor]
        mock_repository.find_all.assert_called_once_with(0, 10)

    @pytest.mark.asyncio
    async def test_search_vendors_use_case(self, sample_vendor, mock_vendor_repository):
        """Test searching vendors"""
        mock_vendor_repository.search_vendors.return_value = [sample_vendor]
        
        use_case = SearchVendorsUseCase(mock_vendor_repository)
        result = await use_case.execute("Acme", ["name"], 10)
        
        assert result == [sample_vendor]
        mock_vendor_repository.search_vendors.assert_called_once_with("Acme", ["name"], 10)


@pytest.mark.unit
class TestVendorService:
    """Test Vendor service"""

    @pytest.mark.asyncio
    async def test_create_vendor_service(self, sample_vendor_data):
        """Test creating vendor through service"""
        mock_repository = Mock()
        mock_repository.exists_by_email = AsyncMock(return_value=False)
        mock_repository.save = AsyncMock(return_value=Vendor(
            name=sample_vendor_data["name"],
            email=sample_vendor_data["email"]
        ))
        
        service = VendorService(mock_repository)
        result = await service.create_vendor(
            name=sample_vendor_data["name"],
            email=sample_vendor_data["email"]
        )
        
        assert result.name == sample_vendor_data["name"]
        mock_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_vendor_service(self, sample_vendor):
        """Test getting vendor through service"""
        vendor_id = uuid4()
        mock_repository = Mock()
        mock_repository.find_by_id = AsyncMock(return_value=sample_vendor)
        
        service = VendorService(mock_repository)
        result = await service.get_vendor(vendor_id)
        
        assert result == sample_vendor
        mock_repository.find_by_id.assert_called_once_with(vendor_id)

    @pytest.mark.asyncio
    async def test_list_vendors_service(self, sample_vendor):
        """Test listing vendors through service"""
        mock_repository = Mock()
        mock_repository.find_all = AsyncMock(return_value=[sample_vendor])
        
        service = VendorService(mock_repository)
        result = await service.list_vendors(skip=0, limit=10)
        
        assert result == [sample_vendor]
        mock_repository.find_all.assert_called_once_with(0, 10)

    @pytest.mark.asyncio
    async def test_search_vendors_service(self, sample_vendor, mock_vendor_repository):
        """Test searching vendors through service"""
        mock_vendor_repository.search_vendors.return_value = [sample_vendor]
        
        service = VendorService(mock_vendor_repository)
        result = await service.search_vendors("supplier", ["name"], 5)
        
        assert result == [sample_vendor]
        mock_vendor_repository.search_vendors.assert_called_once_with("supplier", ["name"], 5)

    @pytest.mark.asyncio
    async def test_get_vendors_by_city_service(self, sample_vendor):
        """Test getting vendors by city through service"""
        city = "Chicago"
        mock_repository = Mock()
        mock_repository.find_by_city = AsyncMock(return_value=[sample_vendor])
        
        service = VendorService(mock_repository)
        result = await service.get_vendors_by_city(city)
        
        assert result == [sample_vendor]
        mock_repository.find_by_city.assert_called_once_with(city, None)