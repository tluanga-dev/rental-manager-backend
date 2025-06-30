"""Tests for SalesReturnItem entity"""

import pytest
from uuid import uuid4

from src.domain.entities.sales import SalesReturnItem


class TestSalesReturnItem:
    """Test suite for SalesReturnItem entity"""
    
    def test_create_sales_return_item(self):
        """Test creating a sales return item"""
        return_id = uuid4()
        sales_item_id = uuid4()
        
        item = SalesReturnItem(
            sales_return_id=return_id,
            sales_item_id=sales_item_id,
            quantity=2,
            condition="GOOD",
            serial_numbers=["SN001", "SN002"]
        )
        
        assert item.sales_return_id == return_id
        assert item.sales_item_id == sales_item_id
        assert item.quantity == 2
        assert item.condition == "GOOD"
        assert item.serial_numbers == ["SN001", "SN002"]
        assert item.is_active is True
    
    def test_is_resellable_good_condition(self):
        """Test resellable check for good condition"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=1,
            condition="good"
        )
        
        assert item.is_resellable() is True
    
    def test_is_resellable_damaged_condition(self):
        """Test resellable check for damaged condition"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=1,
            condition="DAMAGED"
        )
        
        assert item.is_resellable() is False
    
    def test_is_resellable_defective_condition(self):
        """Test resellable check for defective condition"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=1,
            condition="DEFECTIVE"
        )
        
        assert item.is_resellable() is False
    
    def test_is_resellable_case_insensitive(self):
        """Test resellable check is case insensitive"""
        # Test various case variations
        conditions_resellable = ["good", "Good", "GOOD", "gOOd", "like new", "excellent"]
        for condition in conditions_resellable:
            item = SalesReturnItem(
                sales_return_id=uuid4(),
                sales_item_id=uuid4(),
                quantity=1,
                condition=condition
            )
            assert item.is_resellable() is True
        
        conditions_not_resellable = ["damaged", "Damaged", "DAMAGED", "defective", "DEFECTIVE", "poor", "broken"]
        for condition in conditions_not_resellable:
            item = SalesReturnItem(
                sales_return_id=uuid4(),
                sales_item_id=uuid4(),
                quantity=1,
                condition=condition
            )
            assert item.is_resellable() is False
    
    def test_return_item_without_serial_numbers(self):
        """Test return item for bulk items without serial numbers"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=10,
            condition="good",
            serial_numbers=[]
        )
        
        assert item.quantity == 10
        assert item.serial_numbers == []
        assert item.is_resellable() is True
    
    def test_partial_return_quantity(self):
        """Test returning partial quantity"""
        # Customer bought 5, returning 2
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=2,
            condition="GOOD",
            serial_numbers=["SN003", "SN004"]  # Only 2 of the 5 serial numbers
        )
        
        assert item.quantity == 2
        assert len(item.serial_numbers) == 2
    
    def test_single_item_return(self):
        """Test returning a single item"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=1,
            condition="DAMAGED",
            serial_numbers=["SN12345"]
        )
        
        assert item.quantity == 1
        assert item.serial_numbers == ["SN12345"]
        assert item.is_resellable() is False
    
    def test_condition_variations(self):
        """Test various condition descriptions"""
        conditions = [
            ("good", True),
            ("like new", True),
            ("excellent", True),
            ("new", True),
            ("unopened", True),
            ("damaged", False),
            ("defective", False),
            ("broken", False),
            ("poor", False),
            ("opened but not good", False)
        ]
        
        for condition, expected_resellable in conditions:
            item = SalesReturnItem(
                sales_return_id=uuid4(),
                sales_item_id=uuid4(),
                quantity=1,
                condition=condition
            )
            assert item.is_resellable() == expected_resellable
    
    def test_return_item_with_multiple_serials(self):
        """Test return item with multiple serial numbers"""
        serial_numbers = ["SN100", "SN101", "SN102", "SN103", "SN104"]
        
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=5,
            condition="GOOD",
            serial_numbers=serial_numbers
        )
        
        assert item.quantity == 5
        assert len(item.serial_numbers) == 5
        assert all(sn in item.serial_numbers for sn in serial_numbers)
    
    def test_empty_condition(self):
        """Test item with empty condition string"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=1,
            condition="",
            serial_numbers=[]
        )
        
        # Empty condition is not "GOOD"
        assert item.is_resellable() is False
    
    def test_condition_with_whitespace(self):
        """Test condition with whitespace"""
        item = SalesReturnItem(
            sales_return_id=uuid4(),
            sales_item_id=uuid4(),
            quantity=1,
            condition="  good  ",
            serial_numbers=[]
        )
        
        # The implementation does condition.lower() but doesn't strip whitespace
        # So "  good  " won't match "good"
        assert item.is_resellable() is False
        
        # Test without whitespace
        item.condition = "good"
        assert item.is_resellable() is True