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
    repo.find_by_subcategory = AsyncMock()
    repo.find_by_tracking_type = AsyncMock()
    repo.find_consumables = AsyncMock()
    repo.update_quantity = AsyncMock()
    repo.count = AsyncMock()
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


# Additional fixtures for comprehensive inventory item master testing
@pytest.fixture
def sample_inventory_item_bulk_data():
    """Sample bulk inventory item data for testing"""
    return {
        "name": "Steel Screws M6x20",
        "sku": "SCREW-M6-20",
        "description": "Stainless steel screws M6x20mm",
        "tracking_type": "BULK",
        "brand": "FastenerPro",
        "quantity": 500,
        "is_consumable": False,
        "renting_period": 1
    }


@pytest.fixture
def sample_inventory_item_consumable_data():
    """Sample consumable inventory item data for testing"""
    return {
        "name": "A4 Paper Sheets",
        "sku": "PAPER-A4-001",
        "description": "High quality A4 paper for printing",
        "tracking_type": "BULK",
        "brand": "OfficeMax",
        "quantity": 1000,
        "is_consumable": True,
        "renting_period": 1
    }


@pytest.fixture
def sample_inventory_item_individual_data():
    """Sample individual tracking inventory item data for testing"""
    return {
        "name": "Dell Monitor 27-inch",
        "sku": "DELL-MON-27",
        "description": "Dell 27-inch 4K monitor",
        "tracking_type": "INDIVIDUAL",
        "brand": "Dell",
        "manufacturer_part_number": "U2720Q",
        "weight": Decimal("5.8"),
        "length": Decimal("61.1"),
        "width": Decimal("52.1"),
        "height": Decimal("18.6"),
        "quantity": 10,
        "renting_period": 7
    }


@pytest.fixture
def sample_inventory_item_bulk(sample_inventory_item_bulk_data, sample_subcategory):
    """Sample bulk inventory item entity for testing"""
    return InventoryItemMaster(
        inventory_id=uuid4(),
        name=sample_inventory_item_bulk_data["name"],
        sku=sample_inventory_item_bulk_data["sku"],
        description=sample_inventory_item_bulk_data["description"],
        item_sub_category_id=sample_subcategory.id,
        unit_of_measurement_id=uuid4(),
        tracking_type=sample_inventory_item_bulk_data["tracking_type"],
        brand=sample_inventory_item_bulk_data["brand"],
        quantity=sample_inventory_item_bulk_data["quantity"],
        is_consumable=sample_inventory_item_bulk_data["is_consumable"],
        renting_period=sample_inventory_item_bulk_data["renting_period"]
    )


@pytest.fixture
def sample_inventory_item_consumable(sample_inventory_item_consumable_data, sample_subcategory):
    """Sample consumable inventory item entity for testing"""
    return InventoryItemMaster(
        inventory_id=uuid4(),
        name=sample_inventory_item_consumable_data["name"],
        sku=sample_inventory_item_consumable_data["sku"],
        description=sample_inventory_item_consumable_data["description"],
        item_sub_category_id=sample_subcategory.id,
        unit_of_measurement_id=uuid4(),
        tracking_type=sample_inventory_item_consumable_data["tracking_type"],
        brand=sample_inventory_item_consumable_data["brand"],
        quantity=sample_inventory_item_consumable_data["quantity"],
        is_consumable=sample_inventory_item_consumable_data["is_consumable"],
        renting_period=sample_inventory_item_consumable_data["renting_period"]
    )


@pytest.fixture
def sample_inventory_item_individual(sample_inventory_item_individual_data, sample_subcategory):
    """Sample individual tracking inventory item entity for testing"""
    return InventoryItemMaster(
        inventory_id=uuid4(),
        name=sample_inventory_item_individual_data["name"],
        sku=sample_inventory_item_individual_data["sku"],
        description=sample_inventory_item_individual_data["description"],
        item_sub_category_id=sample_subcategory.id,
        unit_of_measurement_id=uuid4(),
        tracking_type=sample_inventory_item_individual_data["tracking_type"],
        brand=sample_inventory_item_individual_data["brand"],
        manufacturer_part_number=sample_inventory_item_individual_data["manufacturer_part_number"],
        weight=sample_inventory_item_individual_data["weight"],
        length=sample_inventory_item_individual_data["length"],
        width=sample_inventory_item_individual_data["width"],
        height=sample_inventory_item_individual_data["height"],
        quantity=sample_inventory_item_individual_data["quantity"],
        renting_period=sample_inventory_item_individual_data["renting_period"]
    )


@pytest.fixture
def multiple_inventory_items(sample_inventory_item, sample_inventory_item_bulk, 
                           sample_inventory_item_consumable, sample_inventory_item_individual):
    """Multiple inventory items for batch testing"""
    return [
        sample_inventory_item,
        sample_inventory_item_bulk,
        sample_inventory_item_consumable,
        sample_inventory_item_individual
    ]


@pytest.fixture
def inventory_item_update_data():
    """Sample data for updating inventory items"""
    return {
        "name": "Updated Item Name",
        "description": "Updated description",
        "brand": "Updated Brand",
        "weight": Decimal("3.5"),
        "length": Decimal("25.0"),
        "width": Decimal("15.0"),
        "height": Decimal("5.0"),
        "quantity": 25,
        "renting_period": 14
    }


@pytest.fixture
def inventory_item_minimal_update_data():
    """Minimal data for updating inventory items"""
    return {
        "name": "Minimally Updated Item",
        "is_active": False
    }


@pytest.fixture
def inventory_item_dimensions_data():
    """Sample dimensions data for testing"""
    return {
        "weight": Decimal("2.5"),
        "length": Decimal("30.0"),
        "width": Decimal("20.0"),
        "height": Decimal("3.0")
    }


@pytest.fixture
def inventory_item_search_queries():
    """Sample search queries for testing"""
    return [
        "MacBook",
        "laptop",
        "Apple",
        "MBP",
        "steel",
        "paper",
        "monitor"
    ]


@pytest.fixture
def inventory_tracking_types():
    """Valid tracking types for testing"""
    return ["BULK", "INDIVIDUAL"]


@pytest.fixture
def invalid_tracking_types():
    """Invalid tracking types for testing"""
    return ["INVALID", "bulk", "individual", "SERIAL", "BATCH"]


@pytest.fixture
def inventory_item_validation_test_cases():
    """Test cases for inventory item validation"""
    return [
        {
            "description": "Empty name",
            "data": {"name": "", "sku": "TEST-001"},
            "expected_error": "Item name is required"
        },
        {
            "description": "Empty SKU",
            "data": {"name": "Test Item", "sku": ""},
            "expected_error": "SKU is required"
        },
        {
            "description": "Invalid tracking type",
            "data": {"name": "Test Item", "sku": "TEST-001", "tracking_type": "INVALID"},
            "expected_error": "Tracking type must be either BULK or INDIVIDUAL"
        },
        {
            "description": "Negative renting period",
            "data": {"name": "Test Item", "sku": "TEST-001", "renting_period": 0},
            "expected_error": "Renting period must be at least 1 day"
        },
        {
            "description": "Negative quantity",
            "data": {"name": "Test Item", "sku": "TEST-001", "quantity": -1},
            "expected_error": "Quantity cannot be negative"
        },
        {
            "description": "Negative weight",
            "data": {"name": "Test Item", "sku": "TEST-001", "weight": Decimal("-1.0")},
            "expected_error": "Weight cannot be negative"
        }
    ]


@pytest.fixture
def inventory_item_test_scenarios():
    """Test scenarios for comprehensive testing"""
    return {
        "create_scenarios": [
            {
                "name": "Basic laptop",
                "sku": "LAPTOP-001",
                "tracking_type": "INDIVIDUAL",
                "expected_success": True
            },
            {
                "name": "Bulk screws",
                "sku": "SCREW-001", 
                "tracking_type": "BULK",
                "quantity": 100,
                "expected_success": True
            },
            {
                "name": "Consumable paper",
                "sku": "PAPER-001",
                "tracking_type": "BULK",
                "is_consumable": True,
                "expected_success": True
            }
        ],
        "update_scenarios": [
            {
                "field": "name",
                "new_value": "Updated Name",
                "expected_success": True
            },
            {
                "field": "quantity",
                "new_value": 50,
                "expected_success": True
            },
            {
                "field": "tracking_type", 
                "new_value": "INVALID",
                "expected_success": False
            }
        ]
    }


# Mock service fixtures
@pytest.fixture
def mock_inventory_service():
    """Mock inventory item master service for testing"""
    service = Mock()
    service.create_inventory_item_master = AsyncMock()
    service.get_inventory_item_master = AsyncMock()
    service.get_inventory_item_master_by_sku = AsyncMock()
    service.update_inventory_item_master = AsyncMock()
    service.delete_inventory_item_master = AsyncMock()
    service.list_inventory_item_masters = AsyncMock()
    service.list_by_subcategory = AsyncMock()
    service.list_by_tracking_type = AsyncMock()
    service.list_consumables = AsyncMock()
    service.search_inventory_item_masters = AsyncMock()
    service.update_quantity = AsyncMock()
    service.update_dimensions = AsyncMock()
    service.count_inventory_item_masters = AsyncMock()
    return service