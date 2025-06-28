import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.domain.entities.id_manager import IdManager
from src.application.services.id_manager_service import IdManagerService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def id_manager_service(mock_repository):
    return IdManagerService(mock_repository)


@pytest.mark.asyncio
async def test_generate_id_success(id_manager_service, mock_repository):
    # Arrange
    prefix = "PUR"
    
    # Mock ID manager entity
    id_manager = IdManager(prefix=prefix, latest_id="PUR-AAA0001")
    id_manager.generate_next_id = lambda: "PUR-AAA0002"
    
    mock_repository.get_or_create_by_prefix.return_value = id_manager
    mock_repository.update.return_value = id_manager

    # Act
    result = await id_manager_service.generate_id(prefix)

    # Assert
    assert result == "PUR-AAA0002"
    mock_repository.get_or_create_by_prefix.assert_called_once_with(prefix)
    mock_repository.update.assert_called_once_with(id_manager)


@pytest.mark.asyncio
async def test_get_current_id_exists(id_manager_service, mock_repository):
    # Arrange
    prefix = "SAL"
    id_manager = IdManager(prefix=prefix, latest_id="SAL-AAA0005")
    mock_repository.get_by_prefix.return_value = id_manager

    # Act
    result = await id_manager_service.get_current_id(prefix)

    # Assert
    assert result == "SAL-AAA0005"
    mock_repository.get_by_prefix.assert_called_once_with(prefix)


@pytest.mark.asyncio
async def test_get_current_id_not_exists(id_manager_service, mock_repository):
    # Arrange
    prefix = "INV"
    mock_repository.get_by_prefix.return_value = None

    # Act
    result = await id_manager_service.get_current_id(prefix)

    # Assert
    assert result is None
    mock_repository.get_by_prefix.assert_called_once_with(prefix)


def test_id_manager_entity_increment_letters():
    # Test letter sequence incrementing
    assert IdManager._increment_letters("A") == "B"
    assert IdManager._increment_letters("Z") == "AA"
    assert IdManager._increment_letters("AZ") == "BA"
    assert IdManager._increment_letters("ZZ") == "AAA"
    assert IdManager._increment_letters("ZZZ") == "AAAA"


def test_id_manager_entity_increment_id():
    # Test ID incrementing
    id_manager = IdManager(prefix="TEST", latest_id="TEST-AAA0001")
    
    # Test number increment
    result = id_manager._increment_id("TEST-AAA0001", "TEST")
    assert result == "TEST-AAA0002"
    
    # Test number overflow with letter increment
    result = id_manager._increment_id("TEST-AAA9999", "TEST")
    assert result == "TEST-AAB0001"
    
    # Test letter overflow
    result = id_manager._increment_id("TEST-ZZZ9999", "TEST")
    assert result == "TEST-AAAA0001"


def test_id_manager_entity_validation():
    # Test empty prefix
    with pytest.raises(ValueError, match="Prefix cannot be empty"):
        IdManager(prefix="")

    # Test invalid prefix characters
    with pytest.raises(ValueError, match="Prefix can only contain uppercase letters, numbers, and underscores"):
        IdManager(prefix="test-invalid")

    # Test long prefix
    long_prefix = "X" * 256
    with pytest.raises(ValueError, match="Prefix cannot exceed 255 characters"):
        IdManager(prefix=long_prefix)


def test_id_manager_entity_generate_next_id():
    # Test normal ID generation
    id_manager = IdManager(prefix="TEST", latest_id="TEST-AAA0001")
    next_id = id_manager.generate_next_id()
    assert next_id == "TEST-AAA0002"
    assert id_manager.latest_id == "TEST-AAA0002"


def test_id_manager_entity_invalid_id_format():
    # Test handling of corrupted ID
    id_manager = IdManager(prefix="TEST", latest_id="INVALID-FORMAT")
    next_id = id_manager.generate_next_id()
    # Should reset to default format
    assert next_id == "TEST-AAA0001"


def test_id_manager_entity_properties():
    id_manager = IdManager(prefix="TEST", latest_id="TEST-AAA0001")
    
    assert id_manager.prefix == "TEST"
    assert id_manager.latest_id == "TEST-AAA0001"


def test_id_manager_entity_update_latest_id():
    id_manager = IdManager(prefix="TEST", latest_id="TEST-AAA0001")
    
    id_manager.update_latest_id("TEST-BBB0005")
    assert id_manager.latest_id == "TEST-BBB0005"


def test_id_manager_entity_health_check_info():
    id_manager = IdManager(prefix="TEST", latest_id="TEST-AAA0001")
    
    health_info = id_manager.get_health_check_info()
    
    assert health_info['prefix'] == "TEST"
    assert health_info['latest_id'] == "TEST-AAA0001"
    assert health_info['is_active'] is True
    assert 'created_at' in health_info
    assert 'updated_at' in health_info


def test_id_manager_entity_string_representation():
    id_manager = IdManager(prefix="TEST", latest_id="TEST-AAA0001")
    
    assert str(id_manager) == "TEST: TEST-AAA0001"
    assert "TEST" in repr(id_manager)
    assert "TEST-AAA0001" in repr(id_manager)


@pytest.mark.asyncio
async def test_reset_sequence_with_custom_value(id_manager_service, mock_repository):
    # Arrange
    prefix = "RST"
    id_manager = IdManager(prefix=prefix, latest_id="RST-AAA0001")
    mock_repository.get_by_prefix.return_value = id_manager
    mock_repository.update.return_value = id_manager

    # Act
    result = await id_manager_service.reset_sequence(prefix, "RST-ZZZ9999")

    # Assert
    assert result == "RST-ZZZ9999"
    mock_repository.get_by_prefix.assert_called_once_with(prefix)
    mock_repository.update.assert_called_once_with(id_manager)


@pytest.mark.asyncio
async def test_reset_sequence_invalid_format(id_manager_service, mock_repository):
    # Arrange
    prefix = "RST"
    id_manager = IdManager(prefix=prefix, latest_id="RST-AAA0001")
    mock_repository.get_by_prefix.return_value = id_manager

    # Act & Assert
    with pytest.raises(ValueError, match="Reset ID must start with 'RST-'"):
        await id_manager_service.reset_sequence(prefix, "INVALID-AAA0001")


@pytest.mark.asyncio
async def test_bulk_generate_ids(id_manager_service, mock_repository):
    # Arrange
    prefix = "BULK"
    id_manager = IdManager(prefix=prefix, latest_id="BULK-AAA0001")
    
    # Mock the generate_id method to return sequential IDs
    call_count = 0
    async def mock_generate_id(p):
        nonlocal call_count
        call_count += 1
        return f"BULK-AAA{call_count:04d}"
    
    id_manager_service.generate_id = mock_generate_id

    # Act
    result = await id_manager_service.bulk_generate_ids(prefix, 3)

    # Assert
    assert len(result) == 3
    assert result == ["BULK-AAA0001", "BULK-AAA0002", "BULK-AAA0003"]


@pytest.mark.asyncio
async def test_bulk_generate_ids_invalid_count(id_manager_service, mock_repository):
    prefix = "BULK"
    
    # Test zero count
    with pytest.raises(ValueError, match="Count must be greater than 0"):
        await id_manager_service.bulk_generate_ids(prefix, 0)
    
    # Test too many
    with pytest.raises(ValueError, match="Cannot generate more than 1000 IDs at once"):
        await id_manager_service.bulk_generate_ids(prefix, 1001)
