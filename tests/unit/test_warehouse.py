import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.entities.warehouse import Warehouse
from src.application.services.warehouse_service import WarehouseService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def warehouse_service(mock_repository):
    return WarehouseService(mock_repository)


@pytest.mark.asyncio
async def test_create_warehouse_success(warehouse_service, mock_repository):
    # Arrange
    name = "Main Warehouse"
    label = "MAIN_WH"
    remarks = "Primary storage facility"
    created_by = "test_user"

    mock_repository.get_by_label.return_value = None
    mock_repository.create.return_value = Warehouse(
        name=name,
        label=label,
        remarks=remarks,
        entity_id=uuid4(),
        created_by=created_by,
    )

    # Act
    result = await warehouse_service.create_warehouse(
        name=name,
        label=label,
        remarks=remarks,
        created_by=created_by,
    )

    # Assert
    assert result.name == name
    assert result.label == label.upper()
    assert result.remarks == remarks
    assert result.created_by == created_by
    mock_repository.get_by_label.assert_called_once_with(label)
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_warehouse_duplicate_label(warehouse_service, mock_repository):
    # Arrange
    name = "Main Warehouse"
    label = "MAIN_WH"

    existing_warehouse = Warehouse(
        name="Existing Warehouse",
        label=label,
        entity_id=uuid4(),
    )
    mock_repository.get_by_label.return_value = existing_warehouse

    # Act & Assert
    with pytest.raises(ValueError, match="Warehouse with label 'MAIN_WH' already exists"):
        await warehouse_service.create_warehouse(
            name=name,
            label=label,
        )

    mock_repository.get_by_label.assert_called_once_with(label)
    mock_repository.create.assert_not_called()


def test_warehouse_entity_validation():
    # Test empty name
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Warehouse(name="", label="TEST")

    # Test empty label
    with pytest.raises(ValueError, match="Label cannot be empty"):
        Warehouse(name="Test Warehouse", label="")

    # Test long name
    long_name = "x" * 256
    with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
        Warehouse(name=long_name, label="TEST")

    # Test long label
    long_label = "x" * 256
    with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
        Warehouse(name="Test Warehouse", label=long_label)


def test_warehouse_label_normalization():
    # Test label is normalized to uppercase
    warehouse = Warehouse(name="Test Warehouse", label="main_warehouse")
    assert warehouse.label == "MAIN_WAREHOUSE"

    # Test label with mixed case
    warehouse = Warehouse(name="Test Warehouse", label="Mixed_Case_Label")
    assert warehouse.label == "MIXED_CASE_LABEL"


def test_warehouse_properties():
    warehouse = Warehouse(
        name="Main Warehouse",
        label="MAIN_WH",
        remarks="Primary storage facility"
    )
    
    assert warehouse.name == "Main Warehouse"
    assert warehouse.label == "MAIN_WH"
    assert warehouse.remarks == "Primary storage facility"


def test_warehouse_update_methods():
    warehouse = Warehouse(
        name="Main Warehouse",
        label="MAIN_WH",
        remarks="Primary storage facility"
    )
    
    # Test update name
    warehouse.update_name("Updated Warehouse")
    assert warehouse.name == "Updated Warehouse"
    
    # Test update label
    warehouse.update_label("updated_wh")
    assert warehouse.label == "UPDATED_WH"
    
    # Test update remarks
    warehouse.update_remarks("Updated remarks")
    assert warehouse.remarks == "Updated remarks"
    
    # Test clear remarks
    warehouse.update_remarks(None)
    assert warehouse.remarks is None


def test_warehouse_string_representation():
    warehouse = Warehouse(
        name="Main Warehouse",
        label="MAIN_WH",
        remarks="Primary storage facility"
    )
    
    assert str(warehouse) == "Main Warehouse"
    assert "Main Warehouse" in repr(warehouse)
    assert "MAIN_WH" in repr(warehouse)
