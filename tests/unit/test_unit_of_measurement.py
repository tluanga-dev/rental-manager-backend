import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.entities.unit_of_measurement import UnitOfMeasurement
from src.application.services.unit_of_measurement_service import UnitOfMeasurementService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def unit_service(mock_repository):
    return UnitOfMeasurementService(mock_repository)


@pytest.mark.asyncio
async def test_create_unit_of_measurement_success(unit_service, mock_repository):
    # Arrange
    name = "Kilogram"
    abbreviation = "kg"
    description = "Unit of mass"
    created_by = "test_user"

    mock_repository.get_by_name.return_value = None
    mock_repository.get_by_abbreviation.return_value = None
    mock_repository.create.return_value = UnitOfMeasurement(
        name=name,
        abbreviation=abbreviation,
        description=description,
        entity_id=uuid4(),
        created_by=created_by,
    )

    # Act
    result = await unit_service.create_unit_of_measurement(
        name=name,
        abbreviation=abbreviation,
        description=description,
        created_by=created_by,
    )

    # Assert
    assert result.name == name
    assert result.abbreviation == abbreviation
    assert result.description == description
    assert result.created_by == created_by
    mock_repository.get_by_name.assert_called_once_with(name)
    mock_repository.get_by_abbreviation.assert_called_once_with(abbreviation)
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_unit_duplicate_name(unit_service, mock_repository):
    # Arrange
    name = "Kilogram"
    abbreviation = "kg"

    existing_unit = UnitOfMeasurement(
        name=name,
        abbreviation="kg2",
        entity_id=uuid4(),
    )
    mock_repository.get_by_name.return_value = existing_unit

    # Act & Assert
    with pytest.raises(ValueError, match="Unit of measurement with name 'Kilogram' already exists"):
        await unit_service.create_unit_of_measurement(
            name=name,
            abbreviation=abbreviation,
        )

    mock_repository.get_by_name.assert_called_once_with(name)
    mock_repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_create_unit_duplicate_abbreviation(unit_service, mock_repository):
    # Arrange
    name = "Kilogram"
    abbreviation = "kg"

    existing_unit = UnitOfMeasurement(
        name="Existing Unit",
        abbreviation=abbreviation,
        entity_id=uuid4(),
    )
    mock_repository.get_by_name.return_value = None
    mock_repository.get_by_abbreviation.return_value = existing_unit

    # Act & Assert
    with pytest.raises(ValueError, match="Unit of measurement with abbreviation 'kg' already exists"):
        await unit_service.create_unit_of_measurement(
            name=name,
            abbreviation=abbreviation,
        )

    mock_repository.get_by_name.assert_called_once_with(name)
    mock_repository.get_by_abbreviation.assert_called_once_with(abbreviation)
    mock_repository.create.assert_not_called()


def test_unit_of_measurement_entity_validation():
    # Test empty name
    with pytest.raises(ValueError, match="Name cannot be empty"):
        UnitOfMeasurement(name="", abbreviation="kg")

    # Test empty abbreviation
    with pytest.raises(ValueError, match="Abbreviation cannot be empty"):
        UnitOfMeasurement(name="Kilogram", abbreviation="")

    # Test long name
    long_name = "x" * 256
    with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
        UnitOfMeasurement(name=long_name, abbreviation="kg")

    # Test long abbreviation
    long_abbreviation = "x" * 9
    with pytest.raises(ValueError, match="Abbreviation cannot exceed 8 characters"):
        UnitOfMeasurement(name="Kilogram", abbreviation=long_abbreviation)


def test_unit_of_measurement_properties():
    # Test successful creation
    unit = UnitOfMeasurement(
        name="Kilogram",
        abbreviation="kg",
        description="Unit of mass"
    )
    
    assert unit.name == "Kilogram"
    assert unit.abbreviation == "kg"
    assert unit.description == "Unit of mass"


def test_unit_of_measurement_update_methods():
    unit = UnitOfMeasurement(
        name="Kilogram",
        abbreviation="kg",
        description="Unit of mass"
    )
    
    # Test update name
    unit.update_name("Gram")
    assert unit.name == "Gram"
    
    # Test update abbreviation
    unit.update_abbreviation("g")
    assert unit.abbreviation == "g"
    
    # Test update description
    unit.update_description("Updated description")
    assert unit.description == "Updated description"
    
    # Test clear description
    unit.update_description(None)
    assert unit.description is None


def test_unit_of_measurement_string_representation():
    unit = UnitOfMeasurement(
        name="Kilogram",
        abbreviation="kg",
        description="Unit of mass"
    )
    
    assert str(unit) == "Kilogram"
    assert "Kilogram" in repr(unit)
    assert "kg" in repr(unit)
