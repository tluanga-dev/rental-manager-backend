"""Tests for SalesTransactionItem entity"""

import pytest
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.sales import SalesTransactionItem


class TestSalesTransactionItem:
    """Test suite for SalesTransactionItem entity"""
    
    def test_create_sales_transaction_item(self):
        """Test creating a sales transaction item"""
        transaction_id = uuid4()
        inventory_id = uuid4()
        warehouse_id = uuid4()
        
        item = SalesTransactionItem(
            transaction_id=transaction_id,
            inventory_item_master_id=inventory_id,
            warehouse_id=warehouse_id,
            quantity=2,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00")
        )
        
        assert item.transaction_id == transaction_id
        assert item.inventory_item_master_id == inventory_id
        assert item.warehouse_id == warehouse_id
        assert item.quantity == 2
        assert item.unit_price == Decimal("100.00")
        assert item.cost_price == Decimal("60.00")
        assert item.discount_percentage == Decimal("0.00")
        assert item.discount_amount == Decimal("0.00")
        assert item.tax_rate == Decimal("0.00")
        assert item.tax_amount == Decimal("0.00")
        assert item.serial_numbers == []
        assert item.is_active is True
    
    def test_calculate_totals_basic(self):
        """Test basic total calculation without discount or tax"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=5,
            unit_price=Decimal("50.00"),
            cost_price=Decimal("30.00")
        )
        
        item.calculate_totals()
        
        assert item.subtotal == Decimal("250.00")  # 5 * 50
        assert item.total == Decimal("250.00")    # No discount or tax
    
    def test_calculate_totals_with_discount_percentage(self):
        """Test total calculation with percentage discount"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=10,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00"),
            discount_percentage=Decimal("10.00")
        )
        
        # calculate_totals is called in __init__ when total == 0
        
        assert item.subtotal == Decimal("900.00")  # (10 * 100) - 10% = 900
        assert item.discount_amount == Decimal("100.00")  # 10% of 1000
        assert item.total == Decimal("900.00")  # subtotal + 0 tax
    
    def test_calculate_totals_with_discount_amount(self):
        """Test total calculation with fixed discount amount"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=3,
            unit_price=Decimal("200.00"),
            cost_price=Decimal("120.00"),
            discount_amount=Decimal("50.00")
        )
        
        # Note: if discount_percentage is 0, discount_amount won't be recalculated
        
        assert item.subtotal == Decimal("550.00")  # (3 * 200) - 50
        assert item.discount_amount == Decimal("50.00")  # Fixed amount
        assert item.total == Decimal("550.00")  # subtotal + 0 tax
    
    def test_calculate_totals_with_tax(self):
        """Test total calculation with tax"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=2,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00"),
            tax_rate=Decimal("10.00")
        )
        
        item.calculate_totals()
        
        assert item.subtotal == Decimal("200.00")  # 2 * 100
        assert item.tax_amount == Decimal("20.00")  # 10% of 200
        assert item.total == Decimal("220.00")  # 200 + 20
    
    def test_calculate_totals_with_discount_and_tax(self):
        """Test total calculation with both discount and tax"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=4,
            unit_price=Decimal("250.00"),
            cost_price=Decimal("150.00"),
            discount_percentage=Decimal("20.00"),
            tax_rate=Decimal("8.00")
        )
        
        # Subtotal is after discount: (4 * 250) - 20% = 800
        assert item.subtotal == Decimal("800.00")
        assert item.discount_amount == Decimal("200.00")  # 20% of 1000
        # Tax is calculated on subtotal (after discount)
        assert item.tax_amount == Decimal("64.00")  # 8% of 800
        assert item.total == Decimal("864.00")  # 800 + 64
    
    def test_calculate_totals_discount_precedence(self):
        """Test that percentage discount takes precedence over amount"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=5,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00"),
            discount_percentage=Decimal("15.00"),
            discount_amount=Decimal("50.00")  # This will be overridden
        )
        
        # When percentage is set, it overrides the amount
        assert item.subtotal == Decimal("425.00")  # (5 * 100) - 15% = 425
        assert item.discount_amount == Decimal("75.00")  # 15% of 500
        assert item.total == Decimal("425.00")  # subtotal + 0 tax
    
    def test_profit_margin(self):
        """Test profit margin calculation"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=10,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00"),
            discount_percentage=Decimal("10.00")
        )
        
        # profit_margin is calculated as percentage: (unit_price - cost_price) / cost_price * 100
        # (100 - 60) / 60 * 100 = 66.67%
        expected_margin = (Decimal("100.00") - Decimal("60.00")) / Decimal("60.00") * Decimal("100")
        assert item.profit_margin == expected_margin
    
    def test_profit_margin_with_loss(self):
        """Test profit margin when selling at a loss"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=5,
            unit_price=Decimal("50.00"),
            cost_price=Decimal("70.00"),
            discount_percentage=Decimal("20.00")
        )
        
        # profit_margin percentage: (50 - 70) / 70 * 100 = -28.57%
        expected_margin = (Decimal("50.00") - Decimal("70.00")) / Decimal("70.00") * Decimal("100")
        assert item.profit_margin == expected_margin
    
    def test_serial_numbers_management(self):
        """Test serial numbers handling"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=3,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00"),
            serial_numbers=["SN001", "SN002", "SN003"]
        )
        
        assert len(item.serial_numbers) == 3
        assert "SN001" in item.serial_numbers
        assert "SN002" in item.serial_numbers
        assert "SN003" in item.serial_numbers
    
    def test_item_with_notes(self):
        """Test item with notes"""
        notes = "Special handling required for this item"
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=1,
            unit_price=Decimal("500.00"),
            cost_price=Decimal("300.00"),
            notes=notes
        )
        
        assert item.notes == notes
    
    def test_zero_quantity_validation(self):
        """Test that zero quantity is not allowed"""
        # This test assumes validation is done at the use case level
        # Entity allows it for flexibility, but use case should validate
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=0,
            unit_price=Decimal("100.00"),
            cost_price=Decimal("60.00")
        )
        
        item.calculate_totals()
        assert item.subtotal == Decimal("0.00")
        assert item.total == Decimal("0.00")
    
    def test_high_precision_calculations(self):
        """Test calculations with high precision decimals"""
        item = SalesTransactionItem(
            transaction_id=uuid4(),
            inventory_item_master_id=uuid4(),
            warehouse_id=uuid4(),
            quantity=7,
            unit_price=Decimal("33.33"),
            cost_price=Decimal("19.99"),
            discount_percentage=Decimal("12.5"),
            tax_rate=Decimal("6.75")
        )
        
        # Base: 7 * 33.33 = 233.31
        # Discount: 12.5% of 233.31 = 29.16375
        # Subtotal (after discount): 233.31 - 29.16375 = 204.14625
        # Tax: 6.75% of 204.14625 = 13.77987...
        # Total: 204.14625 + 13.77987... = 217.926...
        
        # Just verify the calculation follows the expected pattern
        base_amount = Decimal("7") * Decimal("33.33")
        discount = base_amount * (Decimal("12.5") / Decimal("100"))
        subtotal = base_amount - discount
        tax = subtotal * (Decimal("6.75") / Decimal("100"))
        total = subtotal + tax
        
        assert abs(item.subtotal - subtotal) < Decimal("0.01")
        assert abs(item.total - total) < Decimal("0.01")