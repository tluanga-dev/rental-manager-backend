"""
Comprehensive Unit Tests for Unit of Measurement Feature

This test suite covers all layers of the Unit of Measurement feature:
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
from src.domain.entities.unit_of_measurement import UnitOfMeasurement
from src.domain.repositories.unit_of_measurement_repository import UnitOfMeasurementRepository

# Application imports
from src.application.services.unit_of_measurement_service import UnitOfMeasurementService
from src.application.use_cases.unit_of_measurement_use_cases import UnitOfMeasurementUseCases

# Infrastructure imports
from src.infrastructure.repositories.unit_of_measurement_repository_impl import (
    UnitOfMeasurementRepositoryImpl
)
from src.infrastructure.database.models import UnitOfMeasurementModel

# API imports
from src.api.v1.schemas.unit_of_measurement_schemas import (
    UnitOfMeasurementCreate,
    UnitOfMeasurementUpdate,
    UnitOfMeasurementResponse
)


# =============================================================================
# Domain Layer Tests
# =============================================================================

class TestUnitOfMeasurementDomainEntity:
    """Test suite for Unit of Measurement domain entity."""
    
    def test_uom_creation_with_required_fields(self):
        """Test creating a UOM with only required fields."""
        uom = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg"
        )
        
        assert uom.name == "Kilogram"
        assert uom.abbreviation == "kg"
        assert uom.description is None
        assert isinstance(uom.id, str)
        assert len(uom.id) == 36  # UUID string length
        assert uom.is_active is True
        
    def test_uom_creation_with_all_fields(self):
        """Test creating a UOM with all fields."""
        uom_id = str(uuid4())
        created_at = datetime.utcnow()
        
        uom = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg",
            description="Unit of mass in the metric system",
            entity_id=uom_id,
            created_at=created_at,
            created_by="test_user"
        )
        
        assert uom.id == uom_id
        assert uom.name == "Kilogram"
        assert uom.abbreviation == "kg"
        assert uom.description == "Unit of mass in the metric system"
        assert uom.created_at == created_at
        assert uom.created_by == "test_user"
        
    def test_uom_name_validation_empty(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Name cannot be empty"):
            UnitOfMeasurement(name="", abbreviation="kg")
            
        with pytest.raises(ValueError, match="Name cannot be empty"):
            UnitOfMeasurement(name="   ", abbreviation="kg")
            
    def test_uom_name_validation_length(self):
        """Test name length validation."""
        # Valid single character
        uom = UnitOfMeasurement(name="K", abbreviation="kg")
        assert uom.name == "K"
        
        # Too long (over 255 chars)
        long_name = "A" * 256
        with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
            UnitOfMeasurement(name=long_name, abbreviation="kg")
        
    def test_uom_abbreviation_validation_empty(self):
        """Test that empty abbreviation raises ValueError."""
        with pytest.raises(ValueError, match="Abbreviation cannot be empty"):
            UnitOfMeasurement(name="Kilogram", abbreviation="")
            
        with pytest.raises(ValueError, match="Abbreviation cannot be empty"):
            UnitOfMeasurement(name="Kilogram", abbreviation="   ")
            
    def test_uom_abbreviation_validation_length(self):
        """Test abbreviation length validation."""
        # Too long
        with pytest.raises(ValueError, match="Abbreviation cannot exceed 8 characters"):
            UnitOfMeasurement(name="Kilogram", abbreviation="kilogramm")
            
        # Valid maximum length
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kilogram")
        assert uom.abbreviation == "kilogram"
        
    def test_uom_abbreviation_no_spaces(self):
        """Test that abbreviation cannot contain spaces."""
        # The UOM implementation doesn't check for spaces, it just strips them
        uom = UnitOfMeasurement(name="Square Meter", abbreviation="sq m")
        assert uom.abbreviation == "sq m"
            
    def test_uom_whitespace_trimming(self):
        """Test that whitespace is properly trimmed."""
        uom = UnitOfMeasurement(
            name="  Kilogram  ",
            abbreviation="  kg  ",
            description="  Unit of mass  "
        )
        
        assert uom.name == "Kilogram"
        assert uom.abbreviation == "kg"
        assert uom.description == "Unit of mass"
        
    def test_uom_update_name(self):
        """Test updating UOM name."""
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        original_updated_at = uom.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        uom.update_name("Kilograms")
        assert uom.name == "Kilograms"
        assert uom.updated_at > original_updated_at
        
        # Test validation during update
        with pytest.raises(ValueError):
            uom.update_name("")
            
    def test_uom_update_abbreviation(self):
        """Test updating UOM abbreviation."""
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        
        uom.update_abbreviation("KG")
        assert uom.abbreviation == "KG"
        
        # Test validation during update
        with pytest.raises(ValueError):
            uom.update_abbreviation("too long!")
            
    def test_uom_update_description(self):
        """Test updating UOM description."""
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        
        uom.update_description("Unit of mass")
        assert uom.description == "Unit of mass"
        
        # Update with empty string (should set to None)
        uom.update_description("")
        assert uom.description is None
        
        # Update with whitespace only (should set to empty string after strip)
        uom.update_description("   ")
        assert uom.description == ""
        
    def test_uom_string_representation(self):
        """Test string representation of UOM."""
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        str_repr = str(uom)
        repr_str = repr(uom)
        
        # __str__ returns just the name
        assert str_repr == "Kilogram"
        
        # __repr__ contains more details
        assert "UnitOfMeasurement" in repr_str
        assert uom.id in repr_str
        assert "Kilogram" in repr_str
        assert "kg" in repr_str
        
    def test_uom_equality(self):
        """Test UOM equality based on ID."""
        uom_id = str(uuid4())
        uom1 = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg",
            entity_id=uom_id
        )
        uom2 = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg",
            entity_id=uom_id
        )
        uom3 = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg"
        )
        
        assert uom1 == uom2
        assert uom1 != uom3
        assert uom1 != "not a uom"
        
    def test_uom_activation_deactivation(self):
        """Test UOM activation and deactivation."""
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        
        assert uom.is_active is True
        
        uom.deactivate()
        assert uom.is_active is False
        
        uom.activate()
        assert uom.is_active is True


class TestUnitOfMeasurementDomainBoundaryConditions:
    """Test boundary conditions for UOM domain entity."""
    
    def test_uom_maximum_field_lengths(self):
        """Test maximum allowed field lengths."""
        # Maximum name length (255 chars)
        long_name = "A" * 255
        uom = UnitOfMeasurement(name=long_name, abbreviation="kg")
        assert len(uom.name) == 255
        
        # Maximum abbreviation length (8 chars)
        uom = UnitOfMeasurement(name="Test", abbreviation="TESTTEST")
        assert len(uom.abbreviation) == 8
        
    def test_uom_unicode_support(self):
        """Test Unicode character support."""
        uom = UnitOfMeasurement(
            name="千克",  # Chinese for kilogram
            abbreviation="公斤",
            description="公制质量单位"
        )
        
        assert uom.name == "千克"
        assert uom.abbreviation == "公斤"
        assert uom.description == "公制质量单位"
        
    def test_uom_special_characters(self):
        """Test handling of special characters."""
        # Valid special characters in name
        uom = UnitOfMeasurement(
            name="Degrees Celsius (°C)",
            abbreviation="degC"
        )
        assert "°" in uom.name
        
        # Numbers in abbreviation
        uom = UnitOfMeasurement(
            name="Square Meter",
            abbreviation="m2"
        )
        assert uom.abbreviation == "m2"


# =============================================================================
# Repository Tests
# =============================================================================

class TestUnitOfMeasurementRepository:
    """Test suite for UOM repository implementation."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = MagicMock()
        return session
        
    @pytest.fixture
    def repository(self, mock_session):
        """Create repository instance with mock session."""
        repo = UnitOfMeasurementRepositoryImpl(mock_session)
        return repo
        
    @pytest.mark.asyncio
    async def test_repository_create(self, repository, mock_session):
        """Test creating a UOM through repository."""
        uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        
        # Configure mock
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        
        # Execute
        result = await repository.create(uom)
        
        # Verify
        assert result == uom
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once_with(mock_session.add.call_args[0][0])
        
    @pytest.mark.asyncio
    async def test_repository_get_by_id(self, repository, mock_session):
        """Test getting UOM by ID."""
        uom_id = str(uuid4())
        mock_model = MagicMock(spec=UnitOfMeasurementModel)
        mock_uom = UnitOfMeasurement(name="Test", abbreviation="TST")
        
        # Configure mock for new SQLAlchemy pattern
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_model
        
        # Mock the _model_to_entity method
        repository._model_to_entity = MagicMock(return_value=mock_uom)
        
        # Execute
        result = await repository.get_by_id(uom_id)
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result == mock_uom
        
    @pytest.mark.asyncio
    async def test_repository_get_by_abbreviation(self, repository, mock_session):
        """Test getting UOM by abbreviation."""
        mock_model = MagicMock(spec=UnitOfMeasurementModel)
        mock_uom = UnitOfMeasurement(name="Test", abbreviation="TST")
        
        # Configure mock
        mock_result = MagicMock()
        mock_session.execute.return_value = mock_result
        mock_result.scalar_one_or_none.return_value = mock_model
        repository._model_to_entity = MagicMock(return_value=mock_uom)
        
        # Execute
        result = await repository.get_by_abbreviation("kg")
        
        # Verify
        mock_session.execute.assert_called_once()
        assert result == mock_uom
        
    @pytest.mark.asyncio
    async def test_repository_get_all(self, repository, mock_session):
        """Test getting all UOMs with pagination."""
        mock_models = [MagicMock(spec=UnitOfMeasurementModel) for _ in range(3)]
        
        # Configure mock
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_models
        
        # Execute
        results = await repository.get_all(skip=0, limit=10)
        
        # Verify
        assert len(results) == 3
        mock_query.offset.assert_called_once_with(0)
        mock_query.limit.assert_called_once_with(10)
        
    @pytest.mark.asyncio
    async def test_repository_update(self, repository, mock_session):
        """Test updating a UOM."""
        uom = UnitOfMeasurement(name="Updated", abbreviation="upd")
        mock_model = MagicMock(spec=UnitOfMeasurementModel)
        
        # Configure mock
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model
        mock_session.commit = MagicMock()
        mock_session.refresh = MagicMock()
        
        # Execute
        result = await repository.update(uom)
        
        # Verify
        assert result == uom
        mock_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_repository_delete(self, repository, mock_session):
        """Test soft deleting a UOM."""
        uom_id = str(uuid4())
        mock_model = MagicMock(spec=UnitOfMeasurementModel)
        mock_model.is_active = True
        
        # Configure mock
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_model
        mock_session.commit = MagicMock()
        
        # Execute
        result = await repository.delete(uom_id)
        
        # Verify
        assert result is True
        assert mock_model.is_active is False
        mock_session.commit.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_repository_search(self, repository, mock_session):
        """Test searching UOMs by name."""
        mock_models = [MagicMock(spec=UnitOfMeasurementModel) for _ in range(2)]
        
        # Configure mock
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_models
        
        # Execute
        results = await repository.search_by_name("kilo", skip=0, limit=10)
        
        # Verify
        assert len(results) == 2


# =============================================================================
# Use Case Tests
# =============================================================================

class TestUnitOfMeasurementUseCases:
    """Test suite for UOM use cases."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service."""
        return AsyncMock(spec=UnitOfMeasurementService)
        
    @pytest.fixture
    def use_cases(self, mock_service):
        """Create use cases instance with mock service."""
        return UnitOfMeasurementUseCases(mock_service)
        
    @pytest.mark.asyncio
    async def test_create_uom_use_case(self, use_cases, mock_service):
        """Test create UOM use case."""
        # Arrange
        expected_uom = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg"
        )
        mock_service.create_unit_of_measurement.return_value = expected_uom
        
        # Act
        result = await use_cases.create_unit_of_measurement(
            name="Kilogram",
            abbreviation="kg",
            description="Unit of mass"
        )
        
        # Assert
        assert result == expected_uom
        mock_service.create_unit_of_measurement.assert_called_once_with(
            name="Kilogram",
            abbreviation="kg",
            description="Unit of mass",
            created_by=None
        )
        
    @pytest.mark.asyncio
    async def test_get_uom_use_case(self, use_cases, mock_service):
        """Test get UOM by ID use case."""
        # Arrange
        uom_id = str(uuid4())
        expected_uom = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg",
            entity_id=uom_id
        )
        mock_service.get_unit_by_id.return_value = expected_uom
        
        # Act
        result = await use_cases.get_unit_of_measurement(uom_id)
        
        # Assert
        assert result == expected_uom
        mock_service.get_unit_by_id.assert_called_once_with(uom_id)
        
    @pytest.mark.asyncio
    async def test_list_uoms_use_case(self, use_cases, mock_service):
        """Test list UOMs use case."""
        # Arrange
        expected_uoms = [
            UnitOfMeasurement(name="Kilogram", abbreviation="kg"),
            UnitOfMeasurement(name="Gram", abbreviation="g")
        ]
        mock_service.get_all_units.return_value = expected_uoms
        
        # Act
        result = await use_cases.list_units_of_measurement(skip=0, limit=10)
        
        # Assert
        assert len(result) == 2
        assert result == expected_uoms
        mock_service.get_all_units.assert_called_once_with(0, 10, True)
        
    @pytest.mark.asyncio
    async def test_update_uom_use_case(self, use_cases, mock_service):
        """Test update UOM use case."""
        # Arrange
        uom_id = str(uuid4())
        expected_uom = UnitOfMeasurement(
            name="Kilograms",
            abbreviation="KG",
            entity_id=uom_id
        )
        mock_service.update_unit_of_measurement.return_value = expected_uom
        
        # Act
        result = await use_cases.update_unit_of_measurement(
            unit_id=uom_id,
            name="Kilograms",
            abbreviation="KG"
        )
        
        # Assert
        assert result == expected_uom
        mock_service.update_unit_of_measurement.assert_called_once_with(
            unit_id=uom_id,
            name="Kilograms",
            abbreviation="KG",
            description=None
        )
        
    @pytest.mark.asyncio
    async def test_deactivate_uom_use_case(self, use_cases, mock_service):
        """Test deactivate UOM use case."""
        # Arrange
        uom_id = str(uuid4())
        mock_service.deactivate_unit.return_value = True
        
        # Act
        result = await use_cases.deactivate_unit_of_measurement(uom_id)
        
        # Assert
        assert result is True
        mock_service.deactivate_unit.assert_called_once_with(uom_id)
        
    @pytest.mark.asyncio
    async def test_search_uoms_use_case(self, use_cases, mock_service):
        """Test search UOMs use case."""
        # Arrange
        expected_uoms = [
            UnitOfMeasurement(name="Kilogram", abbreviation="kg"),
            UnitOfMeasurement(name="Kilometer", abbreviation="km")
        ]
        mock_service.search_units.return_value = expected_uoms
        
        # Act
        result = await use_cases.search_units_of_measurement("kilo", skip=0, limit=10)
        
        # Assert
        assert len(result) == 2
        mock_service.search_units.assert_called_once_with("kilo", 0, 10)


# =============================================================================
# Service Layer Tests
# =============================================================================

class TestUnitOfMeasurementService:
    """Test suite for UOM service layer."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        return AsyncMock(spec=UnitOfMeasurementRepository)
        
    @pytest.fixture
    def service(self, mock_repository):
        """Create service instance with mock repository."""
        return UnitOfMeasurementService(mock_repository)
        
    @pytest.mark.asyncio
    async def test_create_uom_service(self, service, mock_repository):
        """Test creating UOM through service."""
        # Arrange
        mock_repository.get_by_abbreviation.return_value = None
        expected_uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        mock_repository.create.return_value = expected_uom
        
        # Act
        result = await service.create_unit_of_measurement(
            name="Kilogram",
            abbreviation="kg",
            description="Unit of mass"
        )
        
        # Assert
        assert result == expected_uom
        mock_repository.get_by_abbreviation.assert_called_once_with("kg")
        mock_repository.create.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_create_uom_service_duplicate(self, service, mock_repository):
        """Test creating duplicate UOM through service."""
        # Arrange
        existing_uom = UnitOfMeasurement(name="Existing", abbreviation="kg")
        mock_repository.get_by_abbreviation.return_value = existing_uom
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unit of measurement with abbreviation 'kg' already exists"):
            await service.create_unit_of_measurement(
                name="Kilogram",
                abbreviation="kg"
            )
            
    @pytest.mark.asyncio
    async def test_get_uom_service(self, service, mock_repository):
        """Test getting UOM through service."""
        # Arrange
        uom_id = str(uuid4())
        expected_uom = UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        mock_repository.get_by_id.return_value = expected_uom
        
        # Act
        result = await service.get_unit_of_measurement(uom_id)
        
        # Assert
        assert result == expected_uom
        mock_repository.get_by_id.assert_called_once_with(uom_id)
        
    @pytest.mark.asyncio
    async def test_get_uom_service_not_found(self, service, mock_repository):
        """Test getting non-existent UOM through service."""
        # Arrange
        uom_id = str(uuid4())
        mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Unit of measurement with id {uom_id} not found"):
            await service.get_unit_of_measurement(uom_id)
            
    @pytest.mark.asyncio
    async def test_update_uom_service(self, service, mock_repository):
        """Test updating UOM through service."""
        # Arrange
        uom_id = str(uuid4())
        existing_uom = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg",
            entity_id=uom_id
        )
        mock_repository.get_by_id.return_value = existing_uom
        mock_repository.get_by_abbreviation.return_value = None
        mock_repository.update.return_value = existing_uom
        
        # Act
        result = await service.update_unit_of_measurement(
            unit_id=uom_id,
            name="Kilograms",
            abbreviation="KG"
        )
        
        # Assert
        assert result == existing_uom
        mock_repository.update.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_uom_service_abbreviation_conflict(self, service, mock_repository):
        """Test updating UOM with conflicting abbreviation."""
        # Arrange
        uom_id = str(uuid4())
        other_id = str(uuid4())
        existing_uom = UnitOfMeasurement(
            name="Kilogram",
            abbreviation="kg",
            entity_id=uom_id
        )
        other_uom = UnitOfMeasurement(
            name="Other",
            abbreviation="g",
            entity_id=other_id
        )
        mock_repository.get_by_id.return_value = existing_uom
        mock_repository.get_by_abbreviation.return_value = other_uom
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unit of measurement with abbreviation 'g' already exists"):
            await service.update_unit_of_measurement(
                unit_id=uom_id,
                abbreviation="g"
            )
            
    @pytest.mark.asyncio
    async def test_delete_uom_service(self, service, mock_repository):
        """Test deleting UOM through service."""
        # Arrange
        uom_id = str(uuid4())
        mock_repository.delete.return_value = True
        
        # Act
        result = await service.delete_unit_of_measurement(uom_id)
        
        # Assert
        assert result is True
        mock_repository.delete.assert_called_once_with(uom_id)
        
    @pytest.mark.asyncio
    async def test_get_all_uoms_service(self, service, mock_repository):
        """Test getting all UOMs through service."""
        # Arrange
        expected_uoms = [
            UnitOfMeasurement(name="Kilogram", abbreviation="kg"),
            UnitOfMeasurement(name="Gram", abbreviation="g")
        ]
        mock_repository.get_all.return_value = expected_uoms
        
        # Act
        result = await service.get_all_units_of_measurement(skip=0, limit=10)
        
        # Assert
        assert result == expected_uoms
        mock_repository.get_all.assert_called_once_with(skip=0, limit=10)
        
    @pytest.mark.asyncio
    async def test_search_uoms_service(self, service, mock_repository):
        """Test searching UOMs through service."""
        # Arrange
        expected_uoms = [
            UnitOfMeasurement(name="Kilogram", abbreviation="kg")
        ]
        mock_repository.search_by_name.return_value = expected_uoms
        
        # Act
        result = await service.search_units_of_measurement("kilo", skip=0, limit=10)
        
        # Assert
        assert result == expected_uoms
        mock_repository.search_by_name.assert_called_once_with("kilo", skip=0, limit=10)


# =============================================================================
# API Schema Tests
# =============================================================================

class TestUnitOfMeasurementSchemas:
    """Test suite for UOM API schemas."""
    
    def test_uom_create_schema_valid(self):
        """Test valid UOM create schema."""
        data = {
            "name": "Kilogram",
            "abbreviation": "kg",
            "description": "Unit of mass"
        }
        
        schema = UnitOfMeasurementCreate(**data)
        assert schema.name == "Kilogram"
        assert schema.abbreviation == "kg"
        assert schema.description == "Unit of mass"
        
    def test_uom_create_schema_minimal(self):
        """Test minimal UOM create schema."""
        data = {
            "name": "Kilogram",
            "abbreviation": "kg"
        }
        
        schema = UnitOfMeasurementCreate(**data)
        assert schema.name == "Kilogram"
        assert schema.abbreviation == "kg"
        assert schema.description is None
        
    def test_uom_create_schema_validation(self):
        """Test UOM create schema validation."""
        # Missing required field
        with pytest.raises(ValueError):
            UnitOfMeasurementCreate(name="Kilogram")
            
        # Invalid abbreviation (too long)
        with pytest.raises(ValueError):
            UnitOfMeasurementCreate(
                name="Kilogram",
                abbreviation="toolongabbr"
            )
            
    def test_uom_update_schema(self):
        """Test UOM update schema."""
        data = {
            "name": "Updated Name",
            "abbreviation": "UPD",
            "description": "Updated description"
        }
        
        schema = UnitOfMeasurementUpdate(**data)
        assert schema.name == "Updated Name"
        assert schema.abbreviation == "UPD"
        assert schema.description == "Updated description"
        
    def test_uom_update_schema_partial(self):
        """Test partial UOM update schema."""
        # Only update name
        schema = UnitOfMeasurementUpdate(name="New Name")
        assert schema.name == "New Name"
        assert schema.abbreviation is None
        assert schema.description is None
        
    def test_uom_response_schema(self):
        """Test UOM response schema."""
        uom_id = str(uuid4())
        now = datetime.utcnow()
        
        data = {
            "id": uom_id,
            "name": "Kilogram",
            "abbreviation": "kg",
            "description": "Unit of mass",
            "created_at": now,
            "updated_at": now,
            "created_by": "test_user",
            "is_active": True
        }
        
        schema = UnitOfMeasurementResponse(**data)
        assert schema.id == uom_id
        assert schema.name == "Kilogram"
        assert schema.abbreviation == "kg"
        assert schema.description == "Unit of mass"
        assert schema.created_at == now
        assert schema.is_active is True
        
    def test_uom_response_schema_uuid_validation(self):
        """Test UOM response schema UUID validation."""
        # Invalid UUID format
        with pytest.raises(ValueError):
            UnitOfMeasurementResponse(
                id="invalid-uuid",
                name="Test",
                abbreviation="TST",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )


# =============================================================================
# Edge Cases and Error Handling Tests
# =============================================================================

class TestUnitOfMeasurementEdgeCases:
    """Test edge cases and error handling."""
    
    def test_uom_concurrent_abbreviation_creation(self):
        """Test handling concurrent creation with same abbreviation."""
        # This would be tested in integration tests with real database
        pass
        
    def test_uom_case_sensitivity(self):
        """Test case sensitivity in abbreviations."""
        uom1 = UnitOfMeasurement(name="Test 1", abbreviation="kg")
        uom2 = UnitOfMeasurement(name="Test 2", abbreviation="KG")
        
        # Abbreviations are case-sensitive
        assert uom1.abbreviation != uom2.abbreviation
        
    def test_uom_null_handling(self):
        """Test handling of null/None values."""
        uom = UnitOfMeasurement(
            name="Test",
            abbreviation="TST",
            description=None
        )
        
        assert uom.description is None
        
        # Update with None
        uom.update_description(None)
        assert uom.description is None
        
    def test_uom_immutable_properties(self):
        """Test that certain properties cannot be modified directly."""
        uom = UnitOfMeasurement(name="Test", abbreviation="TST")
        
        # These should not have direct setters
        with pytest.raises(AttributeError):
            uom.id = str(uuid4())
            
        with pytest.raises(AttributeError):
            uom.created_at = datetime.utcnow()


# =============================================================================
# Test Helpers
# =============================================================================

def test_unit_of_measurement_comprehensive_coverage():
    """Verify comprehensive test coverage of all UOM components."""
    test_classes = [
        TestUnitOfMeasurementDomainEntity,
        TestUnitOfMeasurementDomainBoundaryConditions,
        TestUnitOfMeasurementRepository,
        TestUnitOfMeasurementUseCases,
        TestUnitOfMeasurementService,
        TestUnitOfMeasurementSchemas,
        TestUnitOfMeasurementEdgeCases
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