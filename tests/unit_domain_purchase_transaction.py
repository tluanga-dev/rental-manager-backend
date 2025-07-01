"""
Unit tests for Purchase Transaction Domain Layer.

Tests the core business logic without external dependencies:
- PurchaseTransaction Entity behavior
- PurchaseTransactionItem Entity behavior
- Business rules validation
- Domain invariants
- Entity state transitions
"""

import pytest
from datetime import datetime, date, timezone
from decimal import Decimal
from uuid import uuid4
from typing import List

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem


class TestPurchaseTransactionDomainEntity:
    """Test purchase transaction domain entity business logic."""
    
    def test_purchase_transaction_creation_with_required_fields(self):
        """Test creating purchase transaction with only required fields."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-001",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        
        assert transaction.transaction_id == "PUR-001"
        assert transaction.transaction_date == transaction_date
        assert transaction.vendor_id == vendor_id
        assert transaction.total_amount == Decimal("0.00")
        assert transaction.grand_total == Decimal("0.00")
        assert transaction.purchase_order_number is None
        assert transaction.remarks is None
        assert transaction.is_active is True
        assert transaction.id is not None
        assert isinstance(transaction.id, str)
    
    def test_purchase_transaction_creation_with_all_fields(self):
        """Test creating purchase transaction with all fields provided."""
        vendor_id = str(uuid4())
        transaction_id = str(uuid4())
        transaction_date = date.today()
        created_at = datetime.now(timezone.utc)
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-002",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            total_amount=Decimal("1000.50"),
            grand_total=Decimal("1050.75"),
            purchase_order_number="PO-001",
            remarks="Test transaction with all fields",
            entity_id=transaction_id,
            created_at=created_at,
            updated_at=created_at,
            created_by="test_user",
            is_active=True
        )
        
        assert transaction.transaction_id == "PUR-002"
        assert transaction.transaction_date == transaction_date
        assert transaction.vendor_id == vendor_id
        assert transaction.total_amount == Decimal("1000.50")
        assert transaction.grand_total == Decimal("1050.75")
        assert transaction.purchase_order_number == "PO-001"
        assert transaction.remarks == "Test transaction with all fields"
        assert transaction.id == transaction_id
        assert transaction.created_at == created_at
        assert transaction.created_by == "test_user"
    
    def test_transaction_id_validation_empty(self):
        """Test that empty or whitespace-only transaction IDs are rejected."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        invalid_transaction_ids = ["", "   ", "\t", "\n", "  \t\n  "]
        
        for invalid_id in invalid_transaction_ids:
            with pytest.raises(ValueError, match="Transaction ID cannot be empty"):
                PurchaseTransaction(
                    transaction_id=invalid_id,
                    transaction_date=transaction_date,
                    vendor_id=vendor_id
                )
    
    def test_transaction_id_validation_length(self):
        """Test transaction ID length validation."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        # Valid transaction ID at maximum length
        valid_id = "P" * 255
        transaction = PurchaseTransaction(
            transaction_id=valid_id,
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        assert transaction.transaction_id == valid_id
        
        # Invalid transaction ID exceeding maximum length
        invalid_id = "P" * 256
        with pytest.raises(ValueError, match="Transaction ID cannot exceed 255 characters"):
            PurchaseTransaction(
                transaction_id=invalid_id,
                transaction_date=transaction_date,
                vendor_id=vendor_id
            )
    
    def test_transaction_id_whitespace_trimming(self):
        """Test that transaction ID whitespace is properly trimmed."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="  PUR-003  ",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        
        assert transaction.transaction_id == "PUR-003"
    
    def test_amount_validation_negative(self):
        """Test that negative amounts are rejected."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            PurchaseTransaction(
                transaction_id="PUR-004",
                transaction_date=transaction_date,
                vendor_id=vendor_id,
                total_amount=Decimal("-100.00")
            )
        
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            PurchaseTransaction(
                transaction_id="PUR-005",
                transaction_date=transaction_date,
                vendor_id=vendor_id,
                grand_total=Decimal("-50.00")
            )
    
    def test_update_totals(self):
        """Test updating transaction totals."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-006",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        
        # Update totals
        transaction.update_totals(Decimal("500.00"), Decimal("525.00"))
        
        assert transaction.total_amount == Decimal("500.00")
        assert transaction.grand_total == Decimal("525.00")
    
    def test_update_totals_negative_validation(self):
        """Test that update_totals validates negative amounts."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-007",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            transaction.update_totals(Decimal("-100.00"), Decimal("0.00"))
        
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            transaction.update_totals(Decimal("100.00"), Decimal("-50.00"))
    
    def test_business_logic_methods(self):
        """Test business logic methods."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-008",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        
        # All transactions should be editable, cancellable, and allow adding items
        assert transaction.is_editable() is True
        assert transaction.is_cancellable() is True
        assert transaction.can_add_items() is True
    
    def test_transaction_id_display(self):
        """Test transaction ID display property."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-009",
            transaction_date=transaction_date,
            vendor_id=vendor_id
        )
        
        assert transaction.transaction_id_display == "PUR-009"
    
    def test_string_representation(self):
        """Test string representation of purchase transaction."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        transaction = PurchaseTransaction(
            transaction_id="PUR-010",
            transaction_date=transaction_date,
            vendor_id=vendor_id,
            grand_total=Decimal("750.00")
        )
        
        repr_str = repr(transaction)
        assert "PurchaseTransaction" in repr_str
        assert str(transaction.id) in repr_str
        assert "PUR-010" in repr_str
        assert str(vendor_id) in repr_str
        assert "750.00" in repr_str


class TestPurchaseTransactionItemDomainEntity:
    """Test purchase transaction item domain entity business logic."""
    
    def test_purchase_transaction_item_creation_with_required_fields(self):
        """Test creating purchase transaction item with only required fields."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=5,
            unit_price=Decimal("100.00")
        )
        
        assert item.transaction_id == transaction_id
        assert item.inventory_item_id == inventory_item_id
        assert item.quantity == 5
        assert item.unit_price == Decimal("100.00")
        assert item.warehouse_id is None
        assert item.serial_number == []
        assert item.discount == Decimal("0.00")
        assert item.tax_amount == Decimal("0.00")
        assert item.total_price == Decimal("500.00")  # 5 * 100.00
        assert item.remarks is None
        assert item.warranty_period_type is None
        assert item.warranty_period is None
        assert item.is_active is True
        assert item.id is not None
        assert isinstance(item.id, str)
    
    def test_purchase_transaction_item_creation_with_all_fields(self):
        """Test creating purchase transaction item with all fields provided."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        warehouse_id = uuid4()
        item_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("150.00"),
            warehouse_id=warehouse_id,
            serial_number=["SN001", "SN002", "SN003"],
            discount=Decimal("50.00"),
            tax_amount=Decimal("25.00"),
            remarks="Test item with all fields",
            warranty_period_type="MONTHS",
            warranty_period=12,
            entity_id=item_id,
            created_at=created_at,
            updated_at=created_at,
            created_by="test_user",
            is_active=True
        )
        
        assert item.transaction_id == transaction_id
        assert item.inventory_item_id == inventory_item_id
        assert item.warehouse_id == warehouse_id
        assert item.quantity == 3
        assert item.unit_price == Decimal("150.00")
        assert item.serial_number == ["SN001", "SN002", "SN003"]
        assert item.discount == Decimal("50.00")
        assert item.tax_amount == Decimal("25.00")
        assert item.total_price == Decimal("425.00")  # (3 * 150.00) - 50.00 + 25.00
        assert item.remarks == "Test item with all fields"
        assert item.warranty_period_type == "MONTHS"
        assert item.warranty_period == 12
        assert item.id == item_id
        assert item.created_at == created_at
        assert item.created_by == "test_user"
    
    def test_quantity_validation_zero_or_negative(self):
        """Test that zero or negative quantities are rejected."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        invalid_quantities = [0, -1, -10]
        
        for invalid_quantity in invalid_quantities:
            with pytest.raises(ValueError, match="Quantity must be greater than 0"):
                PurchaseTransactionItem(
                    transaction_id=transaction_id,
                    inventory_item_id=inventory_item_id,
                    quantity=invalid_quantity,
                    unit_price=Decimal("100.00")
                )
    
    def test_amount_validation_negative(self):
        """Test that negative amounts are rejected."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        # Test negative unit price
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("-50.00")
            )
        
        # Test negative discount
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                discount=Decimal("-10.00")
            )
        
        # Test negative tax amount
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                tax_amount=Decimal("-5.00")
            )
    
    def test_warranty_period_type_validation(self):
        """Test warranty period type validation."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        # Valid warranty period types
        valid_types = ["DAYS", "MONTHS", "YEARS"]
        for valid_type in valid_types:
            item = PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period_type=valid_type,
                warranty_period=12
            )
            assert item.warranty_period_type == valid_type
        
        # Invalid warranty period type
        with pytest.raises(ValueError, match="Warranty period type must be one of"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period_type="INVALID",
                warranty_period=12
            )
    
    def test_warranty_period_consistency_validation(self):
        """Test that warranty period and type must be provided together."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        # Only type provided, no period
        with pytest.raises(ValueError, match="Both warranty period type and warranty period must be provided together"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period_type="MONTHS"
            )
        
        # Only period provided, no type
        with pytest.raises(ValueError, match="Both warranty period type and warranty period must be provided together"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period=12
            )
        
        # Invalid warranty period (zero or negative)
        with pytest.raises(ValueError, match="Warranty period must be greater than 0"):
            PurchaseTransactionItem(
                transaction_id=transaction_id,
                inventory_item_id=inventory_item_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period_type="MONTHS",
                warranty_period=0
            )
    
    def test_total_price_calculation(self):
        """Test total price calculation."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=4,
            unit_price=Decimal("125.00"),
            discount=Decimal("75.00"),
            tax_amount=Decimal("30.00")
        )
        
        # Total: (4 * 125.00) - 75.00 + 30.00 = 500.00 - 75.00 + 30.00 = 455.00
        assert item.total_price == Decimal("455.00")
    
    def test_total_price_calculation_minimum_zero(self):
        """Test that total price cannot be negative."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=1,
            unit_price=Decimal("50.00"),
            discount=Decimal("100.00"),  # Discount larger than subtotal
            tax_amount=Decimal("10.00")
        )
        
        # Total would be: 50.00 - 100.00 + 10.00 = -40.00, but should be 0.00
        assert item.total_price == Decimal("0.00")
    
    def test_validate_serial_numbers_for_individual_tracking(self):
        """Test serial number validation for individually tracked items."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        # Valid: quantity matches serial numbers
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("100.00"),
            serial_number=["SN001", "SN002", "SN003"]
        )
        item.validate_serial_numbers_for_tracking_type("INDIVIDUAL")  # Should not raise
        
        # Invalid: no serial numbers for individual tracking
        item_no_serials = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=2,
            unit_price=Decimal("100.00")
        )
        with pytest.raises(ValueError, match="Individual tracking items require 2 serial numbers"):
            item_no_serials.validate_serial_numbers_for_tracking_type("INDIVIDUAL")
        
        # Invalid: quantity doesn't match serial numbers
        item_mismatch = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("100.00"),
            serial_number=["SN001", "SN002"]  # Only 2 serial numbers for quantity 3
        )
        with pytest.raises(ValueError, match="Number of serial numbers \\(2\\) must match quantity \\(3\\)"):
            item_mismatch.validate_serial_numbers_for_tracking_type("INDIVIDUAL")
        
        # Invalid: duplicate serial numbers
        item_duplicates = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("100.00"),
            serial_number=["SN001", "SN002", "SN001"]  # Duplicate SN001
        )
        with pytest.raises(ValueError, match="Serial numbers must be unique"):
            item_duplicates.validate_serial_numbers_for_tracking_type("INDIVIDUAL")
    
    def test_validate_serial_numbers_for_bulk_tracking(self):
        """Test serial number validation for bulk tracked items."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        # Valid: no serial numbers for bulk
        item_no_serials = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=10,
            unit_price=Decimal("50.00")
        )
        item_no_serials.validate_serial_numbers_for_tracking_type("BULK")  # Should not raise
        
        # Valid: one serial number for bulk
        item_one_serial = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=10,
            unit_price=Decimal("50.00"),
            serial_number=["BATCH001"]
        )
        item_one_serial.validate_serial_numbers_for_tracking_type("BULK")  # Should not raise
        
        # Invalid: multiple serial numbers for bulk
        item_multiple_serials = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=10,
            unit_price=Decimal("50.00"),
            serial_number=["BATCH001", "BATCH002"]
        )
        with pytest.raises(ValueError, match="Bulk tracked items can have at most one serial number"):
            item_multiple_serials.validate_serial_numbers_for_tracking_type("BULK")
    
    def test_update_pricing(self):
        """Test updating pricing information."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=2,
            unit_price=Decimal("100.00"),
            discount=Decimal("10.00"),
            tax_amount=Decimal("15.00")
        )
        
        # Initial total: (2 * 100.00) - 10.00 + 15.00 = 205.00
        assert item.total_price == Decimal("205.00")
        
        # Update pricing
        item.update_pricing(
            unit_price=Decimal("120.00"),
            discount=Decimal("20.00"),
            tax_amount=Decimal("25.00")
        )
        
        # New total: (2 * 120.00) - 20.00 + 25.00 = 245.00
        assert item.unit_price == Decimal("120.00")
        assert item.discount == Decimal("20.00")
        assert item.tax_amount == Decimal("25.00")
        assert item.total_price == Decimal("245.00")
    
    def test_update_pricing_partial(self):
        """Test updating only some pricing fields."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("80.00"),
            discount=Decimal("15.00"),
            tax_amount=Decimal("12.00")
        )
        
        # Update only unit price
        item.update_pricing(unit_price=Decimal("90.00"))
        
        assert item.unit_price == Decimal("90.00")
        assert item.discount == Decimal("15.00")  # Unchanged
        assert item.tax_amount == Decimal("12.00")  # Unchanged
        assert item.total_price == Decimal("267.00")  # (3 * 90.00) - 15.00 + 12.00
    
    def test_update_warranty(self):
        """Test updating warranty information."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=1,
            unit_price=Decimal("500.00")
        )
        
        # Initially no warranty
        assert item.warranty_period_type is None
        assert item.warranty_period is None
        assert item.has_warranty is False
        
        # Update warranty
        item.update_warranty(warranty_period_type="YEARS", warranty_period=2)
        
        assert item.warranty_period_type == "YEARS"
        assert item.warranty_period == 2
        assert item.has_warranty is True
    
    def test_serial_number_management(self):
        """Test adding and removing serial numbers."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=1,
            unit_price=Decimal("100.00"),
            serial_number=["SN001"]
        )
        
        # Add serial number
        item.add_serial_number("SN002")
        assert "SN002" in item.serial_number
        assert len(item.serial_number) == 2
        
        # Try to add duplicate serial number
        with pytest.raises(ValueError, match="Serial number 'SN001' already exists for this item"):
            item.add_serial_number("SN001")
        
        # Remove serial number
        item.remove_serial_number("SN001")
        assert "SN001" not in item.serial_number
        assert len(item.serial_number) == 1
        
        # Try to remove non-existent serial number
        with pytest.raises(ValueError, match="Serial number 'SN999' not found"):
            item.remove_serial_number("SN999")
    
    def test_calculated_properties(self):
        """Test calculated properties."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=4,
            unit_price=Decimal("125.00"),
            discount=Decimal("100.00"),
            tax_amount=Decimal("50.00"),
            warranty_period_type="MONTHS",
            warranty_period=6
        )
        
        # Test subtotal property
        assert item.subtotal == Decimal("500.00")  # 4 * 125.00
        
        # Test discount percentage property
        assert item.discount_percentage == Decimal("20.00")  # (100.00 / 500.00) * 100
        
        # Test has_warranty property
        assert item.has_warranty is True
        
        # Test item without warranty
        item_no_warranty = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=1,
            unit_price=Decimal("100.00")
        )
        assert item_no_warranty.has_warranty is False
    
    def test_discount_percentage_zero_subtotal(self):
        """Test discount percentage calculation when subtotal is zero."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=1,
            unit_price=Decimal("0.00"),  # Zero unit price
            discount=Decimal("10.00")
        )
        
        assert item.discount_percentage == Decimal("0")
    
    def test_string_representation(self):
        """Test string representation of purchase transaction item."""
        transaction_id = str(uuid4())
        inventory_item_id = uuid4()
        
        item = PurchaseTransactionItem(
            transaction_id=transaction_id,
            inventory_item_id=inventory_item_id,
            quantity=3,
            unit_price=Decimal("150.00")
        )
        
        repr_str = repr(item)
        assert "PurchaseTransactionItem" in repr_str
        assert str(item.id) in repr_str
        assert str(transaction_id) in repr_str
        assert str(inventory_item_id) in repr_str
        assert "3" in repr_str
        assert "450.00" in repr_str  # total_price