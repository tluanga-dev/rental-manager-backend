import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.entities.item_packaging import ItemPackaging
from src.application.services.item_packaging_service import ItemPackagingService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def item_packaging_service(mock_repository):
    return ItemPackagingService(mock_repository)


@pytest.mark.asyncio
async def test_create_item_packaging_success(item_packaging_service, mock_repository):
    # Arrange
    name = "Small Box"
    label = "SMALL_BOX"
    unit = "pieces"
    remarks = "Standard small packaging box"
    created_by = "test_user"

    mock_repository.get_by_label.return_value = None
    mock_repository.create.return_value = ItemPackaging(
        name=name,
        label=label,
        unit=unit,
        remarks=remarks,
        entity_id=uuid4(),
        created_by=created_by,
    )

    # Act
    result = await item_packaging_service.create_item_packaging(
        name=name,
        label=label,
        unit=unit,
        remarks=remarks,
        created_by=created_by,
    )

    # Assert
    assert result.name == name
    assert result.label == label.upper()
    assert result.unit == unit
    assert result.remarks == remarks
    assert result.created_by == created_by
    mock_repository.get_by_label.assert_called_once_with(label)
    mock_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_item_packaging_duplicate_label(item_packaging_service, mock_repository):
    # Arrange
    name = "Small Box"
    label = "SMALL_BOX"
    unit = "pieces"

    existing_packaging = ItemPackaging(
        name="Existing Box",
        label=label,
        unit="pieces",
        entity_id=uuid4(),
    )
    mock_repository.get_by_label.return_value = existing_packaging

    # Act & Assert
    with pytest.raises(ValueError, match="Item packaging with label 'SMALL_BOX' already exists"):
        await item_packaging_service.create_item_packaging(
            name=name,
            label=label,
            unit=unit,
        )

    mock_repository.get_by_label.assert_called_once_with(label)
    mock_repository.create.assert_not_called()


def test_item_packaging_entity_validation():
    # Test empty name
    with pytest.raises(ValueError, match="Name cannot be empty"):
        ItemPackaging(name="", label="TEST", unit="pieces")

    # Test empty label
    with pytest.raises(ValueError, match="Label cannot be empty"):
        ItemPackaging(name="Test", label="", unit="pieces")

    # Test empty unit
    with pytest.raises(ValueError, match="Unit cannot be empty"):
        ItemPackaging(name="Test", label="TEST", unit="")

    # Test long name
    long_name = "x" * 256
    with pytest.raises(ValueError, match="Name cannot exceed 255 characters"):
        ItemPackaging(name=long_name, label="TEST", unit="pieces")

    # Test long label
    long_label = "x" * 256
    with pytest.raises(ValueError, match="Label cannot exceed 255 characters"):
        ItemPackaging(name="Test", label=long_label, unit="pieces")

    # Test long unit
    long_unit = "x" * 256
    with pytest.raises(ValueError, match="Unit cannot exceed 255 characters"):
        ItemPackaging(name="Test", label="TEST", unit=long_unit)


def test_item_packaging_label_normalization():
    # Test label is normalized to uppercase
    packaging = ItemPackaging(name="Test", label="small_box", unit="pieces")
    assert packaging.label == "SMALL_BOX"

    # Test label with mixed case
    packaging = ItemPackaging(name="Test", label="Mixed_Case_Label", unit="pieces")
    assert packaging.label == "MIXED_CASE_LABEL"


def test_item_packaging_string_representation():
    packaging = ItemPackaging(name="Small Box", label="SMALL_BOX", unit="pieces")
    assert str(packaging) == "Small Box"
    assert "Small Box" in repr(packaging)
    assert "SMALL_BOX" in repr(packaging)
    assert "pieces" in repr(packaging)
