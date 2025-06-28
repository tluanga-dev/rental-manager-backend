import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4, UUID
from decimal import Decimal
from datetime import datetime

from src.domain.entities.customer import Customer
from src.domain.entities.vendor import Vendor
from src.domain.entities.warehouse import Warehouse
from src.domain.entities.inventory_item_master import InventoryItemMaster
from src.domain.entities.line_item import LineItem
from src.domain.entities.contact_number import ContactNumber
from src.domain.entities.item_category import ItemCategory, ItemSubCategory
from src.domain.value_objects.address import Address
from src.domain.value_objects.phone_number import PhoneNumber


@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    session = Mock()
    session.add = Mock()
    session.commit = Mock()
    session.refresh = Mock()
    session.query = Mock()
    session.delete = Mock()
    return session


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing"""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "address": "123 Main St",
        "city": "New York",
        "remarks": "Test customer"
    }


@pytest.fixture
def sample_customer(sample_customer_data):
    """Sample customer entity for testing"""
    return Customer(
        customer_id=uuid4(),
        name=sample_customer_data["name"],
        email=sample_customer_data["email"],
        address=sample_customer_data["address"],
        city=sample_customer_data["city"],
        remarks=sample_customer_data["remarks"]
    )


@pytest.fixture
def sample_vendor_data():
    """Sample vendor data for testing"""
    return {
        "name": "Acme Corp",
        "email": "info@acme.com",
        "address": "456 Business Ave",
        "city": "Chicago",
        "remarks": "Reliable supplier"
    }


@pytest.fixture
def sample_vendor(sample_vendor_data):
    """Sample vendor entity for testing"""
    return Vendor(
        vendor_id=uuid4(),
        name=sample_vendor_data["name"],
        email=sample_vendor_data["email"],
        address=sample_vendor_data["address"],
        city=sample_vendor_data["city"],
        remarks=sample_vendor_data["remarks"]
    )


@pytest.fixture
def sample_warehouse_data():
    """Sample warehouse data for testing"""
    return {
        "name": "Main Warehouse",
        "description": "Primary storage facility",
        "address": "789 Storage Rd",
        "city": "Los Angeles",
        "manager_name": "Jane Smith",
        "capacity": 1000
    }


@pytest.fixture
def sample_warehouse(sample_warehouse_data):
    """Sample warehouse entity for testing"""
    return Warehouse(
        entity_id=uuid4(),
        name=sample_warehouse_data["name"],
        label=sample_warehouse_data["name"].upper().replace(" ", "_"),
        remarks=sample_warehouse_data["description"]
    )


@pytest.fixture
def sample_category_data():
    """Sample category data for testing"""
    return {
        "name": "Electronics",
        "abbreviation": "ELEC"
    }


@pytest.fixture
def sample_category(sample_category_data):
    """Sample category entity for testing"""
    return ItemCategory(
        category_id=uuid4(),
        name=sample_category_data["name"],
        abbreviation=sample_category_data["abbreviation"]
    )


@pytest.fixture
def sample_subcategory_data():
    """Sample subcategory data for testing"""
    return {
        "name": "Laptops",
        "abbreviation": "LAPTOP"
    }


@pytest.fixture
def sample_subcategory(sample_subcategory_data, sample_category):
    """Sample subcategory entity for testing"""
    return ItemSubCategory(
        subcategory_id=uuid4(),
        name=sample_subcategory_data["name"],
        abbreviation=sample_subcategory_data["abbreviation"],
        item_category_id=sample_category.id
    )


@pytest.fixture
def sample_inventory_item_data():
    """Sample inventory item data for testing"""
    return {
        "name": "MacBook Pro 16-inch",
        "sku": "MBP16-001",
        "description": "Apple MacBook Pro with M2 chip",
        "tracking_type": "INDIVIDUAL",
        "brand": "Apple",
        "weight": Decimal("2.15"),
        "length": Decimal("35.57"),
        "width": Decimal("24.81"),
        "height": Decimal("1.68"),
        "renting_period": 7,
        "quantity": 5
    }


@pytest.fixture
def sample_inventory_item(sample_inventory_item_data, sample_subcategory, sample_warehouse):
    """Sample inventory item entity for testing"""
    return InventoryItemMaster(
        inventory_id=uuid4(),
        name=sample_inventory_item_data["name"],
        sku=sample_inventory_item_data["sku"],
        description=sample_inventory_item_data["description"],
        item_sub_category_id=sample_subcategory.id,
        unit_of_measurement_id=uuid4(),
        tracking_type=sample_inventory_item_data["tracking_type"],
        brand=sample_inventory_item_data["brand"],
        weight=sample_inventory_item_data["weight"],
        length=sample_inventory_item_data["length"],
        width=sample_inventory_item_data["width"],
        height=sample_inventory_item_data["height"],
        renting_period=sample_inventory_item_data["renting_period"],
        quantity=sample_inventory_item_data["quantity"]
    )


@pytest.fixture
def sample_line_item_data():
    """Sample line item data for testing"""
    return {
        "serial_number": "MBP16-001-SN001",
        "status": "AVAILABLE",
        "rental_rate": Decimal("50.00"),
        "replacement_cost": Decimal("2500.00"),
        "rentable": True,
        "sellable": False
    }


@pytest.fixture
def sample_line_item(sample_line_item_data, sample_inventory_item, sample_warehouse):
    """Sample line item entity for testing"""
    return LineItem(
        id=uuid4(),
        inventory_item_master_id=sample_inventory_item.id,
        warehouse_id=sample_warehouse.id,
        serial_number=sample_line_item_data["serial_number"],
        status=sample_line_item_data["status"],
        rental_rate=sample_line_item_data["rental_rate"],
        replacement_cost=sample_line_item_data["replacement_cost"],
        rentable=sample_line_item_data["rentable"],
        sellable=sample_line_item_data["sellable"]
    )


@pytest.fixture
def sample_contact_number_data():
    """Sample contact number data for testing"""
    return {
        "number": "+1234567890",
        "entity_type": "Customer"
    }


@pytest.fixture
def sample_contact_number(sample_contact_number_data, sample_customer):
    """Sample contact number entity for testing"""
    return ContactNumber(
        contact_id=uuid4(),
        phone_number=PhoneNumber(sample_contact_number_data["number"]),
        entity_type=sample_contact_number_data["entity_type"],
        entity_id=sample_customer.id
    )


@pytest.fixture
def sample_address_data():
    """Sample address data for testing"""
    return {
        "street": "123 Main Street",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
        "country": "USA"
    }


@pytest.fixture
def sample_address(sample_address_data):
    """Sample address value object for testing"""
    return Address(
        street=sample_address_data["street"],
        city=sample_address_data["city"],
        state=sample_address_data["state"],
        zip_code=sample_address_data["zip_code"],
        country=sample_address_data["country"]
    )


# Mock repository fixtures
@pytest.fixture
def mock_customer_repository():
    """Mock customer repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_email = AsyncMock()
    repo.find_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.search = AsyncMock()
    repo.exists_by_email = AsyncMock()
    repo.search_customers = AsyncMock()
    return repo


@pytest.fixture
def mock_inventory_repository():
    """Mock inventory item master repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_sku = AsyncMock()
    repo.find_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.exists_by_sku = AsyncMock()
    repo.exists_by_name = AsyncMock()
    repo.search = AsyncMock()
    return repo


@pytest.fixture
def mock_contact_repository():
    """Mock contact number repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_entity = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_vendor_repository():
    """Mock vendor repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_email = AsyncMock()
    repo.find_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.exists = AsyncMock()
    repo.search_vendors = AsyncMock()
    return repo


@pytest.fixture
def mock_item_category_repository():
    """Mock item category repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_all = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.exists = AsyncMock()
    repo.exists_by_name = AsyncMock()
    repo.exists_by_abbreviation = AsyncMock()
    repo.save_subcategory = AsyncMock()
    repo.find_subcategories_by_category = AsyncMock()
    repo.exists_subcategory_by_name = AsyncMock()
    repo.exists_subcategory_by_abbreviation = AsyncMock()
    repo.exists_by_name_and_category = AsyncMock()
    repo.exists_by_abbreviation_and_category = AsyncMock()
    repo.exists_by_abbreviation = AsyncMock()
    repo.find_by_category = AsyncMock()
    repo.search = AsyncMock()
    repo.search_categories = AsyncMock()
    return repo