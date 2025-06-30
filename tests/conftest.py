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
from src.domain.entities.purchase_order import PurchaseOrder, PurchaseOrderStatus
from src.domain.entities.purchase_order_line_item import PurchaseOrderLineItem
from src.domain.entities.sales import SalesTransaction, SalesTransactionItem, SalesReturn, SalesReturnItem
from src.domain.value_objects.address import Address
from src.domain.value_objects.phone_number import PhoneNumber
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms


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


# Purchase Order Test Fixtures

@pytest.fixture
def sample_purchase_order_data():
    """Sample purchase order data for testing"""
    from datetime import date
    return {
        "order_number": "PO-2024-001",
        "order_date": date.today(),
        "expected_delivery_date": date.today(),
        "reference_number": "REF-001",
        "invoice_number": "INV-001",
        "notes": "Test purchase order",
        "status": PurchaseOrderStatus.DRAFT
    }


@pytest.fixture
def sample_purchase_order(sample_purchase_order_data, sample_vendor):
    """Sample purchase order entity for testing"""
    return PurchaseOrder(
        order_number=sample_purchase_order_data["order_number"],
        vendor_id=sample_vendor.id,
        order_date=sample_purchase_order_data["order_date"],
        expected_delivery_date=sample_purchase_order_data["expected_delivery_date"],
        reference_number=sample_purchase_order_data["reference_number"],
        invoice_number=sample_purchase_order_data["invoice_number"],
        notes=sample_purchase_order_data["notes"],
        created_by="test_user"
    )


@pytest.fixture
def sample_purchase_order_line_item_data():
    """Sample purchase order line item data for testing"""
    return {
        "quantity": 2,
        "unit_price": Decimal("100.00"),
        "discount": Decimal("10.00"),
        "tax_amount": Decimal("18.00"),
        "serial_number": "TEST-SN-001",
        "reference_number": "LINE-REF-001",
        "rental_rate": Decimal("25.00"),
        "replacement_cost": Decimal("500.00"),
        "late_fee_rate": Decimal("5.00"),
        "sell_tax_rate": 10,
        "rent_tax_rate": 8,
        "rentable": True,
        "sellable": False,
        "selling_price": Decimal("150.00")
    }


@pytest.fixture
def sample_purchase_order_line_item(sample_purchase_order_line_item_data, sample_purchase_order, 
                                   sample_inventory_item, sample_warehouse):
    """Sample purchase order line item entity for testing"""
    return PurchaseOrderLineItem(
        purchase_order_id=sample_purchase_order.id,
        inventory_item_master_id=sample_inventory_item.id,
        warehouse_id=sample_warehouse.id,
        quantity=sample_purchase_order_line_item_data["quantity"],
        unit_price=sample_purchase_order_line_item_data["unit_price"],
        discount=sample_purchase_order_line_item_data["discount"],
        tax_amount=sample_purchase_order_line_item_data["tax_amount"],
        serial_number=sample_purchase_order_line_item_data["serial_number"],
        reference_number=sample_purchase_order_line_item_data["reference_number"],
        rental_rate=sample_purchase_order_line_item_data["rental_rate"],
        replacement_cost=sample_purchase_order_line_item_data["replacement_cost"],
        late_fee_rate=sample_purchase_order_line_item_data["late_fee_rate"],
        sell_tax_rate=sample_purchase_order_line_item_data["sell_tax_rate"],
        rent_tax_rate=sample_purchase_order_line_item_data["rent_tax_rate"],
        rentable=sample_purchase_order_line_item_data["rentable"],
        sellable=sample_purchase_order_line_item_data["sellable"],
        selling_price=sample_purchase_order_line_item_data["selling_price"],
        created_by="test_user"
    )


@pytest.fixture
def sample_create_purchase_order_items_data(sample_inventory_item, sample_warehouse):
    """Sample items data for creating purchase order"""
    return [
        {
            "inventory_item_master_id": sample_inventory_item.id,
            "warehouse_id": sample_warehouse.id,
            "quantity": 2,
            "unit_price": 100.00,
            "discount": 10.00,
            "tax_amount": 18.00,
            "serial_number": "TEST-SN-001",
            "rental_rate": 25.00,
            "replacement_cost": 500.00,
            "rentable": True,
            "sellable": False
        },
        {
            "inventory_item_master_id": sample_inventory_item.id,
            "warehouse_id": sample_warehouse.id,
            "quantity": 1,
            "unit_price": 200.00,
            "discount": 0.00,
            "tax_amount": 20.00,
            "serial_number": "TEST-SN-002",
            "rental_rate": 50.00,
            "replacement_cost": 1000.00,
            "rentable": True,
            "sellable": True,
            "selling_price": 250.00
        }
    ]


# Mock Purchase Order Repository Fixtures

@pytest.fixture
def mock_purchase_order_repository():
    """Mock purchase order repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_all = AsyncMock()
    repo.find_by_vendor = AsyncMock()
    repo.find_by_status = AsyncMock()
    repo.find_by_date_range = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_next_order_number = AsyncMock()
    repo.search_purchase_orders = AsyncMock()
    return repo


@pytest.fixture
def mock_purchase_order_line_item_repository():
    """Mock purchase order line item repository for testing"""
    repo = Mock()
    repo.save = AsyncMock()
    repo.find_by_id = AsyncMock()
    repo.find_by_purchase_order = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def purchase_order_test_scenarios():
    """Test scenarios for purchase order testing"""
    return {
        "create_scenarios": [
            {
                "description": "Basic purchase order with single item",
                "expected_success": True,
                "item_count": 1
            },
            {
                "description": "Purchase order with multiple items",
                "expected_success": True,
                "item_count": 3
            },
            {
                "description": "Purchase order with invalid vendor",
                "expected_success": False,
                "error_type": "ValueError"
            }
        ],
        "status_transitions": [
            {
                "from_status": PurchaseOrderStatus.DRAFT,
                "to_status": PurchaseOrderStatus.ORDERED,
                "allowed": True
            },
            {
                "from_status": PurchaseOrderStatus.ORDERED,
                "to_status": PurchaseOrderStatus.RECEIVED,
                "allowed": True
            },
            {
                "from_status": PurchaseOrderStatus.RECEIVED,
                "to_status": PurchaseOrderStatus.DRAFT,
                "allowed": False
            }
        ]
    }


# Sales Module Test Fixtures

@pytest.fixture
def sample_sales_transaction_data():
    """Sample sales transaction data for testing"""
    from datetime import date
    return {
        "transaction_id": "SO-2024-001",
        "invoice_number": "INV-2024-001",
        "order_date": datetime.now(),
        "delivery_date": datetime.now(),
        "status": SalesStatus.DRAFT,
        "payment_status": PaymentStatus.PENDING,
        "payment_terms": PaymentTerms.NET_30,
        "subtotal": Decimal("1000.00"),
        "discount_amount": Decimal("50.00"),
        "tax_amount": Decimal("95.00"),
        "shipping_amount": Decimal("25.00"),
        "grand_total": Decimal("1070.00"),
        "amount_paid": Decimal("0.00"),
        "shipping_address": "123 Shipping St, New York, NY 10001",
        "billing_address": "456 Billing Ave, New York, NY 10002",
        "purchase_order_number": "PO-CUST-001",
        "notes": "Test sales order",
        "customer_notes": "Please deliver before noon"
    }


@pytest.fixture
def sample_sales_transaction(sample_sales_transaction_data, sample_customer):
    """Sample sales transaction entity for testing"""
    data = sample_sales_transaction_data.copy()
    data['customer_id'] = sample_customer.id
    return SalesTransaction(**data)


@pytest.fixture
def sample_sales_transaction_item_data():
    """Sample sales transaction item data for testing"""
    return {
        "quantity": 2,
        "unit_price": Decimal("500.00"),
        "cost_price": Decimal("300.00"),
        "discount_percentage": Decimal("5.00"),
        "discount_amount": Decimal("50.00"),
        "tax_rate": Decimal("10.00"),
        "tax_amount": Decimal("95.00"),
        "subtotal": Decimal("1000.00"),
        "total": Decimal("1045.00"),
        "serial_numbers": ["SN001", "SN002"],
        "notes": "Item in good condition"
    }


@pytest.fixture
def sample_sales_transaction_item(sample_sales_transaction_item_data, sample_sales_transaction, 
                                 sample_inventory_item, sample_warehouse):
    """Sample sales transaction item entity for testing"""
    return SalesTransactionItem(
        transaction_id=sample_sales_transaction.id,
        inventory_item_master_id=sample_inventory_item.id,
        warehouse_id=sample_warehouse.id,
        **sample_sales_transaction_item_data
    )


@pytest.fixture
def sample_sales_return_data():
    """Sample sales return data for testing"""
    return {
        "return_id": "SR-2024-001",
        "return_date": datetime.now(),
        "reason": "Customer changed mind",
        "refund_amount": Decimal("1045.00"),
        "restocking_fee": Decimal("104.50")
    }


@pytest.fixture
def sample_sales_return(sample_sales_return_data, sample_sales_transaction):
    """Sample sales return entity for testing"""
    return SalesReturn(
        sales_transaction_id=sample_sales_transaction.id,
        **sample_sales_return_data
    )


@pytest.fixture
def sample_sales_return_item_data():
    """Sample sales return item data for testing"""
    return {
        "quantity": 1,
        "condition": "GOOD",
        "serial_numbers": ["SN001"]
    }


@pytest.fixture
def sample_sales_return_item(sample_sales_return_item_data, sample_sales_return, 
                            sample_sales_transaction_item):
    """Sample sales return item entity for testing"""
    return SalesReturnItem(
        sales_return_id=sample_sales_return.id,
        sales_item_id=sample_sales_transaction_item.id,
        **sample_sales_return_item_data
    )


# Mock Sales Repositories

@pytest.fixture
def mock_sales_transaction_repository():
    """Mock sales transaction repository for testing"""
    repo = Mock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_transaction_id = AsyncMock()
    repo.get_by_invoice_number = AsyncMock()
    repo.get_by_customer = AsyncMock()
    repo.get_by_status = AsyncMock()
    repo.get_by_payment_status = AsyncMock()
    repo.get_overdue_transactions = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.search = AsyncMock()
    repo.get_next_transaction_id = AsyncMock()
    repo.list = AsyncMock()
    repo.count = AsyncMock()
    repo.get_sales_summary = AsyncMock()
    repo.get_top_customers = AsyncMock()
    repo.get_sales_by_period = AsyncMock()
    return repo


@pytest.fixture
def mock_sales_transaction_item_repository():
    """Mock sales transaction item repository for testing"""
    repo = Mock()
    repo.create = AsyncMock()
    repo.create_many = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_transaction = AsyncMock()
    repo.get_by_inventory_item = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.delete_by_transaction = AsyncMock()
    repo.get_sales_by_item = AsyncMock()
    repo.get_top_selling_items = AsyncMock()
    return repo


@pytest.fixture
def mock_sales_return_repository():
    """Mock sales return repository for testing"""
    repo = Mock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_return_id = AsyncMock()
    repo.get_by_transaction = AsyncMock()
    repo.get_pending_approval = AsyncMock()
    repo.approve = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.list = AsyncMock()
    repo.get_return_summary = AsyncMock()
    repo.get_next_return_id = AsyncMock()
    return repo


@pytest.fixture
def mock_sales_return_item_repository():
    """Mock sales return item repository for testing"""
    repo = Mock()
    repo.create = AsyncMock()
    repo.create_many = AsyncMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_return = AsyncMock()
    repo.get_by_sales_item = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.delete_by_return = AsyncMock()
    return repo


@pytest.fixture
def mock_id_manager_repository():
    """Mock ID manager repository for testing"""
    repo = Mock()
    repo.get_next_id = AsyncMock()
    return repo


@pytest.fixture
def mock_inventory_stock_movement_service():
    """Mock inventory stock movement service for testing"""
    service = Mock()
    service.reserve_stock = AsyncMock()
    service.release_stock = AsyncMock()
    service.confirm_sale = AsyncMock()
    service.process_return = AsyncMock()
    service.check_availability = AsyncMock()
    return service


@pytest.fixture
def sales_transaction_test_data():
    """Test data for sales transaction creation"""
    return {
        "items": [
            {
                "inventory_item_master_id": uuid4(),
                "warehouse_id": uuid4(),
                "quantity": 2,
                "unit_price": 500.00,
                "discount_percentage": 5.0,
                "tax_rate": 10.0,
                "serial_numbers": ["SN001", "SN002"]
            },
            {
                "inventory_item_master_id": uuid4(),
                "warehouse_id": uuid4(),
                "quantity": 1,
                "unit_price": 1000.00,
                "discount_percentage": 0.0,
                "tax_rate": 10.0,
                "serial_numbers": ["SN003"]
            }
        ],
        "shipping_amount": 50.00,
        "payment_terms": "NET_30",
        "shipping_address": "789 Delivery Rd, Chicago, IL 60601",
        "billing_address": "456 Invoice St, Chicago, IL 60602",
        "purchase_order_number": "CUST-PO-123",
        "notes": "Rush delivery requested"
    }


@pytest.fixture
def sales_return_test_data():
    """Test data for sales return creation"""
    return {
        "reason": "Product not as described",
        "items": [
            {
                "sales_item_id": uuid4(),
                "quantity": 1,
                "condition": "GOOD",
                "serial_numbers": ["SN001"]
            }
        ],
        "restocking_fee": 10.0
    }


@pytest.fixture
def sales_status_transitions():
    """Valid sales status transitions for testing"""
    return [
        (SalesStatus.DRAFT, SalesStatus.CONFIRMED, True),
        (SalesStatus.CONFIRMED, SalesStatus.PROCESSING, True),
        (SalesStatus.PROCESSING, SalesStatus.SHIPPED, True),
        (SalesStatus.SHIPPED, SalesStatus.DELIVERED, True),
        (SalesStatus.DRAFT, SalesStatus.CANCELLED, True),
        (SalesStatus.DELIVERED, SalesStatus.DRAFT, False),
        (SalesStatus.CANCELLED, SalesStatus.CONFIRMED, False)
    ]


@pytest.fixture
def payment_status_transitions():
    """Valid payment status transitions for testing"""
    return [
        (PaymentStatus.PENDING, PaymentStatus.PARTIAL, True),
        (PaymentStatus.PARTIAL, PaymentStatus.PAID, True),
        (PaymentStatus.PENDING, PaymentStatus.PAID, True),
        (PaymentStatus.PENDING, PaymentStatus.OVERDUE, True),
        (PaymentStatus.PAID, PaymentStatus.REFUNDED, True),
        (PaymentStatus.PAID, PaymentStatus.PENDING, False),
        (PaymentStatus.REFUNDED, PaymentStatus.PAID, False)
    ]