"""
Test configuration and shared fixtures.
"""

import os
import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from typing import Generator

# Set testing environment variable to ensure SQLite is used
os.environ["TESTING"] = "1"

# Async test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def anyio_backend():
    """Configure async test backend."""
    return "asyncio"


# Database fixtures for integration tests
@pytest.fixture
def sample_warehouse_data():
    """Sample warehouse data for testing."""
    return {
        "name": "Test Warehouse",
        "label": "TEST",
        "remarks": "Sample warehouse for testing",
        "created_by": "test_user"
    }


@pytest.fixture
def sample_warehouse_id():
    """Generate a sample warehouse ID for testing."""
    return str(uuid4())


# Item Category fixtures
@pytest.fixture
def sample_category_data():
    """Sample item category data for testing."""
    return {
        "name": "Test Category",
        "abbreviation": "TEST",
        "created_by": "test_user"
    }


@pytest.fixture
def sample_subcategory_data():
    """Sample item subcategory data for testing."""
    return {
        "name": "Test Subcategory",
        "abbreviation": "TESTSC",  # Exactly 6 characters for subcategory
        "created_by": "test_user"
    }


@pytest.fixture
def sample_category():
    """Create a sample item category for testing."""
    from src.domain.entities.item_category import ItemCategory
    return ItemCategory(
        name="Test Category",
        abbreviation="TEST"
    )


@pytest.fixture
def sample_subcategory():
    """Create a sample item subcategory for testing."""
    from src.domain.entities.item_category import ItemSubCategory
    from uuid import uuid4
    return ItemSubCategory(
        name="Test Subcategory",
        abbreviation="TESTSC",  # Exactly 6 characters
        item_category_id=str(uuid4())
    )


@pytest.fixture
def mock_item_category_repository():
    """Create a mock item category repository."""
    from unittest.mock import AsyncMock
    return AsyncMock()