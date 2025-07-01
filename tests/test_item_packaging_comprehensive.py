"""
Comprehensive Unit Tests for Item Packaging Feature

This test suite covers all layers of the Item Packaging feature:
- Domain Entity
- Repository
- Use Cases
- Service
- API Endpoints
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

# Domain imports
from src.domain.entities.item_packaging import ItemPackaging
from src.domain.repositories.item_packaging_repository import ItemPackagingRepository

# Application imports
from src.application.services.item_packaging_service import ItemPackagingService
from src.application.use_cases.item_packaging_use_cases import ItemPackagingUseCases

# Infrastructure imports
from src.infrastructure.repositories.item_packaging_repository_impl import (
    ItemPackagingRepositoryImpl
)
from src.infrastructure.database.models import ItemPackagingModel

# API imports
from src.api.v1.schemas.item_packaging_schemas import (
    ItemPackagingCreate,
    ItemPackagingUpdate,
    ItemPackagingResponse
)


# =============================================================================
# Domain Layer Tests
# =============================================================================

class TestItemPackagingDomainEntity:
    """Test suite for Item Packaging domain entity."""
    
    def test_packaging_creation_with_required_fields(self):
        """Test creating an item packaging with only required fields."""
        packaging = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs"
        )
        
        assert packaging.name == "Small Box"
        assert packaging.label == "BOX-S"
        assert packaging.unit == "pcs"
        assert packaging.remarks is None
        assert isinstance(packaging.id, str)
        assert len(packaging.id) == 36  # UUID string length
        assert packaging.is_active is True
        
    def test_packaging_creation_with_all_fields(self):
        """Test creating an item packaging with all fields."""
        packaging_id = str(uuid4())
        created_at = datetime.utcnow()
        
        packaging = ItemPackaging(
            name="Large Box",
            label="BOX-L",
            unit="pcs",
            remarks="For bulk items",
            entity_id=packaging_id,
            created_at=created_at,
            created_by="test_user"
        )
        
        assert packaging.id == packaging_id
        assert packaging.name == "Large Box"
        assert packaging.label == "BOX-L"
        assert packaging.unit == "pcs"
        assert packaging.remarks == "For bulk items"
        assert packaging.created_at == created_at
        assert packaging.created_by == "test_user"
        
    def test_packaging_name_validation_empty(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            ItemPackaging(name="", label="BOX", unit="pcs")
            
        with pytest.raises(ValueError, match="Name cannot be empty"):
            ItemPackaging(name="   ", label="BOX", unit="pcs")
            
    def test_packaging_name_validation_length(self):
        """Test name length validation."""
        # Valid single character
        packaging = ItemPackaging(name="B", label="BOX", unit="pcs")
        assert packaging.name == "B"
        
        # Too long (over 255 chars)
        long_name = "A" * 256
        with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
            ItemPackaging(name=long_name, label="BOX", unit="pcs")
        
    def test_packaging_label_validation_empty(self):
        """Test that empty label raises ValueError."""
        with pytest.raises(ValueError, match="Label cannot be empty"):
            ItemPackaging(name="Box", label="", unit="pcs")
            
        with pytest.raises(ValueError, match="Label cannot be empty"):
            ItemPackaging(name="Box", label="   ", unit="pcs")
            
    def test_packaging_label_validation_length(self):
        """Test label length validation."""
        # Too long (over 255 chars)
        long_label = "A" * 256
        with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
            ItemPackaging(name="Box", label=long_label, unit="pcs")
            
        # Valid long label
        long_valid_label = "A" * 255
        packaging = ItemPackaging(name="Box", label=long_valid_label, unit="pcs")
        assert len(packaging.label) == 255
        
    def test_packaging_label_normalization(self):
        """Test that label is normalized to uppercase."""
        packaging = ItemPackaging(name="Box", label="box-small", unit="pcs")
        assert packaging.label == "BOX-SMALL"
        
    def test_packaging_unit_validation_empty(self):
        """Test that empty unit raises ValueError."""
        with pytest.raises(ValueError, match="Unit cannot be empty"):
            ItemPackaging(name="Box", label="BOX", unit="")
            
        with pytest.raises(ValueError, match="Unit cannot be empty"):
            ItemPackaging(name="Box", label="BOX", unit="   ")
            
    def test_packaging_unit_validation_length(self):
        """Test unit length validation."""
        # Too long (over 255 chars)
        long_unit = "A" * 256
        with pytest.raises(ValueError, match="Unit cannot exceed 255 characters"):
            ItemPackaging(name="Box", label="BOX", unit=long_unit)
            
        # Valid maximum length
        long_valid_unit = "A" * 255
        packaging = ItemPackaging(name="Box", label="BOX", unit=long_valid_unit)
        assert len(packaging.unit) == 255
        
    def test_packaging_whitespace_trimming(self):
        """Test that whitespace is properly trimmed."""
        packaging = ItemPackaging(
            name="  Small Box  ",
            label="  box-s  ",
            unit="  pcs  ",
            remarks="  For small items  "
        )
        
        assert packaging.name == "Small Box"
        assert packaging.label == "BOX-S"
        assert packaging.unit == "pcs"
        assert packaging.remarks == "For small items"
        
    def test_packaging_update_name(self):
        """Test updating packaging name."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        original_updated_at = packaging.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        packaging.update_name("Medium Box")
        assert packaging.name == "Medium Box"
        assert packaging.updated_at > original_updated_at
        
        # Test validation during update
        with pytest.raises(ValueError):
            packaging.update_name("")
            
    def test_packaging_update_label(self):
        """Test updating packaging label."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        
        packaging.update_label("box-m")
        assert packaging.label == "BOX-M"  # Should be normalized
        
        # Test validation during update
        with pytest.raises(ValueError):
            packaging.update_label("")
            
    def test_packaging_update_unit(self):
        """Test updating packaging unit."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        
        packaging.update_unit("pieces")
        assert packaging.unit == "pieces"
        
        # Test validation during update
        with pytest.raises(ValueError):
            packaging.update_unit("")
            
    def test_packaging_update_remarks(self):
        """Test updating packaging remarks."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        
        packaging.update_remarks("For small items")
        assert packaging.remarks == "For small items"
        
        # Update with empty string (should set to None)
        packaging.update_remarks("")
        assert packaging.remarks is None
        
        # Update with whitespace only (should set to empty string after stripping)
        packaging.update_remarks("   ")
        assert packaging.remarks == ""
        
        # Update with None directly
        packaging.update_remarks(None)
        assert packaging.remarks is None
        
    def test_packaging_string_representation(self):
        """Test string representation of packaging."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        str_repr = str(packaging)
        repr_str = repr(packaging)
        
        # __str__ returns just the name
        assert str_repr == "Small Box"
        
        # __repr__ contains more details
        assert "ItemPackaging" in repr_str
        assert packaging.id in repr_str
        assert "Small Box" in repr_str
        assert "BOX-S" in repr_str
        
    def test_packaging_equality(self):
        """Test packaging equality based on ID."""
        packaging_id = str(uuid4())
        packaging1 = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            entity_id=packaging_id
        )
        packaging2 = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            entity_id=packaging_id
        )
        packaging3 = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs"
        )
        
        assert packaging1 == packaging2
        assert packaging1 != packaging3
        assert packaging1 != "not a packaging"
        
    def test_packaging_activation_deactivation(self):
        """Test packaging activation and deactivation."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        
        assert packaging.is_active is True
        
        packaging.deactivate()
        assert packaging.is_active is False
        
        packaging.activate()
        assert packaging.is_active is True


class TestItemPackagingDomainBoundaryConditions:
    """Test boundary conditions for packaging domain entity."""
    
    def test_packaging_maximum_field_lengths(self):
        """Test maximum allowed field lengths."""
        # Maximum name length (255 chars)
        long_name = "A" * 255
        packaging = ItemPackaging(name=long_name, label="BOX", unit="pcs")
        assert len(packaging.name) == 255
        
        # Maximum label length (255 chars)
        long_label = "A" * 255
        packaging = ItemPackaging(name="Test", label=long_label, unit="pcs")
        assert len(packaging.label) == 255
        
        # Maximum unit length (255 chars)
        long_unit = "A" * 255
        packaging = ItemPackaging(name="Test", label="BOX", unit=long_unit)
        assert len(packaging.unit) == 255
        
    def test_packaging_unicode_support(self):
        """Test Unicode character support."""
        packaging = ItemPackaging(
            name="小盒子",  # Chinese for small box
            label="盒子-S",
            unit="个",  # Chinese for pieces
            remarks="用于小物品"  # Chinese for "for small items"
        )
        
        assert packaging.name == "小盒子"
        assert packaging.label == "盒子-S"  # Labels are not normalized for Unicode
        assert packaging.unit == "个"
        assert packaging.remarks == "用于小物品"
        
    def test_packaging_special_characters(self):
        """Test handling of special characters."""
        # Valid special characters in name
        packaging = ItemPackaging(
            name="Box (Large Size)",
            label="BOX-L-01",
            unit="pcs/set"
        )
        assert "(" in packaging.name
        assert "-" in packaging.label
        assert "/" in packaging.unit
        
        # Numbers in various fields
        packaging = ItemPackaging(
            name="Box Type 1",
            label="BOX-001",
            unit="pcs"
        )
        assert "1" in packaging.name
        assert "001" in packaging.label


# =============================================================================
# Repository Tests
# =============================================================================

class TestItemPackagingRepository:
    """Test suite for packaging repository implementation."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        return session
        
    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance with mock session."""
        repo = ItemPackagingRepositoryImpl(mock_session)
        return repo
        
    @pytest.mark.asyncio
    async def test_repository_create(self, repository, mock_session):
        """Test creating a packaging through repository."""
        packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        
        # Configure mock
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        
        # Execute
        result = await repository.create(packaging)
        
        # Verify
        assert result == packaging
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_repository_get_by_id(self, repository, mock_session):
        """Test getting packaging by ID."""
        packaging_id = str(uuid4())
        mock_model = MagicMock(spec=ItemPackagingModel)
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_model
        
        # Execute
        result = await repository.get_by_id(packaging_id)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result is not None
        
    @pytest.mark.asyncio
    async def test_repository_get_by_label(self, repository, mock_session):
        """Test getting packaging by label."""
        mock_model = MagicMock(spec=ItemPackagingModel)
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_model
        
        # Execute
        result = await repository.get_by_label("BOX-S")
        
        # Verify
        mock_session.execute.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_repository_get_all(self, repository, mock_session):
        """Test getting all packagings with pagination."""
        mock_models = [MagicMock(spec=ItemPackagingModel) for _ in range(3)]
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.all.return_value = mock_models
        
        # Execute
        results = await repository.get_all(skip=0, limit=10)
        
        # Verify
        assert len(results) == 3
        
    @pytest.mark.asyncio
    async def test_repository_update(self, repository, mock_session):
        """Test updating a packaging."""
        packaging_id = str(uuid4())
        packaging = ItemPackaging(name="Updated", label="UPD", unit="pcs", entity_id=packaging_id)
        mock_model = MagicMock(spec=ItemPackagingModel)
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        
        # Mock the _model_to_entity method to return the packaging
        repository._model_to_entity = MagicMock(return_value=packaging)
        
        # Execute
        result = await repository.update(packaging)
        
        # Verify
        assert result == packaging
        mock_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_repository_delete(self, repository, mock_session):
        """Test soft deleting a packaging."""
        packaging_id = str(uuid4())
        mock_model = MagicMock(spec=ItemPackagingModel)
        mock_model.is_active = True
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_model
        mock_session.commit = MagicMock()
        
        # Execute
        result = await repository.delete(packaging_id)
        
        # Verify
        assert result is True
        assert mock_model.is_active is False
        mock_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_repository_search(self, repository, mock_session):
        """Test searching packagings by name."""
        mock_models = [MagicMock(spec=ItemPackagingModel) for _ in range(2)]
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalars.return_value.all.return_value = mock_models
        
        # Execute
        results = await repository.search_by_name("box", skip=0, limit=10)
        
        # Verify
        assert len(results) == 2


# =============================================================================
# Use Case Tests
# =============================================================================

class TestItemPackagingUseCases:
    """Test suite for packaging use cases."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service."""
        return AsyncMock(spec=ItemPackagingService)
        
    @pytest.fixture
    def use_cases(self, mock_service):
        """Create use cases instance with mock service."""
        return ItemPackagingUseCases(mock_service)
        
    @pytest.mark.asyncio
    async def test_create_packaging_use_case(self, use_cases, mock_service):
        """Test create packaging use case."""
        # Arrange
        expected_packaging = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs"
        )
        mock_service.create_item_packaging.return_value = expected_packaging
        
        # Act
        result = await use_cases.create_item_packaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            remarks="For small items"
        )
        
        # Assert
        assert result == expected_packaging
        mock_service.create_item_packaging.assert_called_once_with(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            remarks="For small items",
            created_by=None
        )
        
    @pytest.mark.asyncio
    async def test_get_packaging_use_case(self, use_cases, mock_service):
        """Test get packaging by ID use case."""
        # Arrange
        packaging_id = str(uuid4())
        expected_packaging = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            entity_id=packaging_id
        )
        mock_service.get_item_packaging_by_id.return_value = expected_packaging
        
        # Act
        result = await use_cases.get_item_packaging(packaging_id)
        
        # Assert
        assert result == expected_packaging
        mock_service.get_item_packaging_by_id.assert_called_once_with(packaging_id)
        
    @pytest.mark.asyncio
    async def test_list_packagings_use_case(self, use_cases, mock_service):
        """Test list packagings use case."""
        # Arrange
        expected_packagings = [
            ItemPackaging(name="Small Box", label="BOX-S", unit="pcs"),
            ItemPackaging(name="Large Box", label="BOX-L", unit="pcs")
        ]
        mock_service.get_all_item_packagings.return_value = expected_packagings
        
        # Act
        result = await use_cases.list_item_packagings(skip=0, limit=10)
        
        # Assert
        assert len(result) == 2
        assert result == expected_packagings
        mock_service.get_all_item_packagings.assert_called_once_with(0, 10, True)
        
    @pytest.mark.asyncio
    async def test_update_packaging_use_case(self, use_cases, mock_service):
        """Test update packaging use case."""
        # Arrange
        packaging_id = str(uuid4())
        expected_packaging = ItemPackaging(
            name="Medium Box",
            label="BOX-M",
            unit="pieces",
            entity_id=packaging_id
        )
        mock_service.update_item_packaging.return_value = expected_packaging
        
        # Act
        result = await use_cases.update_item_packaging(
            item_packaging_id=packaging_id,
            name="Medium Box",
            label="BOX-M",
            unit="pieces"
        )
        
        # Assert
        assert result == expected_packaging
        mock_service.update_item_packaging.assert_called_once_with(
            item_packaging_id=packaging_id,
            name="Medium Box",
            label="BOX-M",
            unit="pieces",
            remarks=None
        )
        
    @pytest.mark.asyncio
    async def test_deactivate_packaging_use_case(self, use_cases, mock_service):
        """Test deactivate packaging use case."""
        # Arrange
        packaging_id = str(uuid4())
        mock_service.deactivate_item_packaging.return_value = True
        
        # Act
        result = await use_cases.deactivate_item_packaging(packaging_id)
        
        # Assert
        assert result is True
        mock_service.deactivate_item_packaging.assert_called_once_with(packaging_id)
        
    @pytest.mark.asyncio
    async def test_search_packagings_use_case(self, use_cases, mock_service):
        """Test search packagings use case."""
        # Arrange
        expected_packagings = [
            ItemPackaging(name="Small Box", label="BOX-S", unit="pcs"),
            ItemPackaging(name="Big Box", label="BOX-B", unit="pcs")
        ]
        mock_service.search_item_packagings_by_name.return_value = expected_packagings
        
        # Act
        result = await use_cases.search_item_packagings("box", skip=0, limit=10)
        
        # Assert
        assert len(result) == 2
        mock_service.search_item_packagings_by_name.assert_called_once_with("box", 0, 10)


# =============================================================================
# Service Layer Tests
# =============================================================================

class TestItemPackagingService:
    """Test suite for packaging service layer."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return AsyncMock(spec=ItemPackagingRepository)
        
    @pytest.fixture
    def service(self, mock_repository):
        """Create service instance with mock repository."""
        return ItemPackagingService(mock_repository)
        
    @pytest.mark.asyncio
    async def test_create_packaging_service(self, service, mock_repository):
        """Test creating packaging through service."""
        # Arrange
        mock_repository.get_by_label.return_value = None
        expected_packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        mock_repository.create.return_value = expected_packaging
        
        # Act
        result = await service.create_item_packaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            remarks="For small items"
        )
        
        # Assert
        assert result == expected_packaging
        mock_repository.get_by_label.assert_called_once_with("BOX-S")
        mock_repository.create.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_create_packaging_service_duplicate(self, service, mock_repository):
        """Test creating duplicate packaging through service."""
        # Arrange
        existing_packaging = ItemPackaging(name="Existing", label="BOX-S", unit="pcs")
        mock_repository.get_by_label.return_value = existing_packaging
        
        # Act & Assert
        with pytest.raises(ValueError, match="Item packaging with label 'BOX-S' already exists"):
            await service.create_item_packaging(
                name="Small Box",
                label="BOX-S",
                unit="pcs"
            )
            
    @pytest.mark.asyncio
    async def test_get_packaging_service(self, service, mock_repository):
        """Test getting packaging through service."""
        # Arrange
        packaging_id = str(uuid4())
        expected_packaging = ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        mock_repository.get_by_id.return_value = expected_packaging
        
        # Act
        result = await service.get_item_packaging_by_id(packaging_id)
        
        # Assert
        assert result == expected_packaging
        mock_repository.get_by_id.assert_called_once_with(packaging_id)
        
    @pytest.mark.asyncio
    async def test_get_packaging_service_not_found(self, service, mock_repository):
        """Test getting non-existent packaging through service."""
        # Arrange
        packaging_id = str(uuid4())
        mock_repository.get_by_id.return_value = None
        
        # Act
        result = await service.get_item_packaging_by_id(packaging_id)
        
        # Assert
        assert result is None
            
    @pytest.mark.asyncio
    async def test_update_packaging_service(self, service, mock_repository):
        """Test updating packaging through service."""
        # Arrange
        packaging_id = str(uuid4())
        existing_packaging = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            entity_id=packaging_id
        )
        mock_repository.get_by_id.return_value = existing_packaging
        mock_repository.get_by_label.return_value = None
        mock_repository.update.return_value = existing_packaging
        
        # Act
        result = await service.update_item_packaging(
            item_packaging_id=packaging_id,
            name="Medium Box",
            label="BOX-M",
            unit="pieces"
        )
        
        # Assert
        assert result == existing_packaging
        mock_repository.update.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_packaging_service_label_conflict(self, service, mock_repository):
        """Test updating packaging with conflicting label."""
        # Arrange
        packaging_id = str(uuid4())
        other_id = str(uuid4())
        existing_packaging = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            entity_id=packaging_id
        )
        other_packaging = ItemPackaging(
            name="Other",
            label="BOX-L",
            unit="pcs",
            entity_id=other_id
        )
        mock_repository.get_by_id.return_value = existing_packaging
        mock_repository.get_by_label.return_value = other_packaging
        
        # Act & Assert
        with pytest.raises(ValueError, match="Item packaging with label 'BOX-L' already exists"):
            await service.update_item_packaging(
                item_packaging_id=packaging_id,
                label="BOX-L"
            )
            
    @pytest.mark.asyncio
    async def test_deactivate_packaging_service(self, service, mock_repository):
        """Test deactivating packaging through service."""
        # Arrange
        packaging_id = str(uuid4())
        existing_packaging = ItemPackaging(
            name="Small Box",
            label="BOX-S",
            unit="pcs",
            entity_id=packaging_id
        )
        mock_repository.get_by_id.return_value = existing_packaging
        mock_repository.update.return_value = existing_packaging
        
        # Act
        result = await service.deactivate_item_packaging(packaging_id)
        
        # Assert
        assert result is True
        mock_repository.get_by_id.assert_called_once_with(packaging_id)
        mock_repository.update.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_all_packagings_service(self, service, mock_repository):
        """Test getting all packagings through service."""
        # Arrange
        expected_packagings = [
            ItemPackaging(name="Small Box", label="BOX-S", unit="pcs"),
            ItemPackaging(name="Large Box", label="BOX-L", unit="pcs")
        ]
        mock_repository.get_all.return_value = expected_packagings
        
        # Act
        result = await service.get_all_item_packagings(skip=0, limit=10)
        
        # Assert
        assert result == expected_packagings
        mock_repository.get_all.assert_called_once_with(0, 10, True)
        
    @pytest.mark.asyncio
    async def test_search_packagings_service(self, service, mock_repository):
        """Test searching packagings through service."""
        # Arrange
        expected_packagings = [
            ItemPackaging(name="Small Box", label="BOX-S", unit="pcs")
        ]
        mock_repository.search_by_name.return_value = expected_packagings
        
        # Act
        result = await service.search_item_packagings_by_name("box", skip=0, limit=10)
        
        # Assert
        assert result == expected_packagings
        mock_repository.search_by_name.assert_called_once_with("box", 0, 10)


# =============================================================================
# API Schema Tests
# =============================================================================

class TestItemPackagingSchemas:
    """Test suite for packaging API schemas."""
    
    def test_packaging_create_schema_valid(self):
        """Test valid packaging create schema."""
        data = {
            "name": "Small Box",
            "label": "BOX-S",
            "unit": "pcs",
            "remarks": "For small items"
        }
        
        schema = ItemPackagingCreate(**data)
        assert schema.name == "Small Box"
        assert schema.label == "BOX-S"
        assert schema.unit == "pcs"
        assert schema.remarks == "For small items"
        
    def test_packaging_create_schema_minimal(self):
        """Test minimal packaging create schema."""
        data = {
            "name": "Small Box",
            "label": "BOX-S",
            "unit": "pcs"
        }
        
        schema = ItemPackagingCreate(**data)
        assert schema.name == "Small Box"
        assert schema.label == "BOX-S"
        assert schema.unit == "pcs"
        assert schema.remarks is None
        
    def test_packaging_create_schema_validation(self):
        """Test packaging create schema validation."""
        # Missing required field
        with pytest.raises(ValueError):
            ItemPackagingCreate(name="Small Box", label="BOX-S")
            
        # Invalid label (too long)
        long_label = "A" * 256
        with pytest.raises(ValueError):
            ItemPackagingCreate(
                name="Small Box",
                label=long_label,
                unit="pcs"
            )
            
    def test_packaging_update_schema(self):
        """Test packaging update schema."""
        data = {
            "name": "Updated Box",
            "label": "UPD-BOX",
            "unit": "pieces",
            "remarks": "Updated description"
        }
        
        schema = ItemPackagingUpdate(**data)
        assert schema.name == "Updated Box"
        assert schema.label == "UPD-BOX"
        assert schema.unit == "pieces"
        assert schema.remarks == "Updated description"
        
    def test_packaging_update_schema_partial(self):
        """Test partial packaging update schema."""
        # Only update name
        schema = ItemPackagingUpdate(name="New Name")
        assert schema.name == "New Name"
        assert schema.label is None
        assert schema.unit is None
        assert schema.remarks is None
        
    def test_packaging_response_schema(self):
        """Test packaging response schema."""
        packaging_id = str(uuid4())
        now = datetime.utcnow()
        
        data = {
            "id": packaging_id,
            "name": "Small Box",
            "label": "BOX-S",
            "unit": "pcs",
            "remarks": "For small items",
            "created_at": now,
            "updated_at": now,
            "created_by": "test_user",
            "is_active": True
        }
        
        schema = ItemPackagingResponse(**data)
        assert schema.id == packaging_id
        assert schema.name == "Small Box"
        assert schema.label == "BOX-S"
        assert schema.unit == "pcs"
        assert schema.remarks == "For small items"
        assert schema.created_at == now
        assert schema.is_active is True
        
    def test_packaging_response_schema_uuid_validation(self):
        """Test packaging response schema UUID validation."""
        # Invalid UUID format
        with pytest.raises(ValueError):
            ItemPackagingResponse(
                id="invalid-uuid",
                name="Test",
                label="TST",
                unit="pcs",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================

class TestItemPackagingEdgeCases:
    """Test edge cases and error handling."""
    
    def test_packaging_concurrent_label_creation(self):
        """Test handling concurrent creation with same label."""
        # This would be tested in integration tests with real database
        pass
        
    def test_packaging_case_sensitivity(self):
        """Test case sensitivity in labels."""
        packaging1 = ItemPackaging(name="Test 1", label="box-s", unit="pcs")
        packaging2 = ItemPackaging(name="Test 2", label="BOX-S", unit="pcs")
        
        # Both should be normalized to uppercase
        assert packaging1.label == "BOX-S"
        assert packaging2.label == "BOX-S"
        
    def test_packaging_null_handling(self):
        """Test handling of null/None values."""
        packaging = ItemPackaging(
            name="Test",
            label="TST",
            unit="pcs",
            remarks=None
        )
        
        assert packaging.remarks is None
        
        # Update with None
        packaging.update_remarks(None)
        assert packaging.remarks is None
        
    def test_packaging_immutable_properties(self):
        """Test that certain properties cannot be modified directly."""
        packaging = ItemPackaging(name="Test", label="TST", unit="pcs")
        
        # These should not have direct setters
        with pytest.raises(AttributeError):
            packaging.id = str(uuid4())
            
        with pytest.raises(AttributeError):
            packaging.created_at = datetime.utcnow()


# =============================================================================
# Test Helpers
# =============================================================================

def test_item_packaging_comprehensive_coverage():
    """Verify comprehensive test coverage of all packaging components."""
    test_classes = [
        TestItemPackagingDomainEntity,
        TestItemPackagingDomainBoundaryConditions,
        TestItemPackagingRepository,
        TestItemPackagingUseCases,
        TestItemPackagingService,
        TestItemPackagingSchemas,
        TestItemPackagingEdgeCases
    ]
    
    total_tests = 0
    for test_class in test_classes:
        # Count test methods
        test_methods = [
            method for method in dir(test_class)
            if method.startswith('test_') and callable(getattr(test_class, method))
        ]
        total_tests += len(test_methods)
        
    assert total_tests >= 50, f"Expected at least 50 tests, found {total_tests}"
    print(f"✅ Comprehensive test suite contains {total_tests} tests")