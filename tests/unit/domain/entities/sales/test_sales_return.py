"""Tests for SalesReturn entity"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.entities.sales import SalesReturn


class TestSalesReturn:
    """Test suite for SalesReturn entity"""
    
    def test_create_sales_return(self):
        """Test creating a sales return"""
        transaction_id = uuid4()
        
        sales_return = SalesReturn(
            sales_transaction_id=transaction_id,
            return_date=datetime.now(),
            reason="Customer changed mind",
            refund_amount=Decimal("500.00"),
            restocking_fee=Decimal("50.00")
        )
        
        assert sales_return.sales_transaction_id == transaction_id
        assert sales_return.reason == "Customer changed mind"
        assert sales_return.refund_amount == Decimal("500.00")
        assert sales_return.restocking_fee == Decimal("50.00")
        assert sales_return.approved_by_id is None
        assert sales_return.is_active is True
    
    def test_net_refund_amount(self):
        """Test net refund calculation"""
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Defective product",
            refund_amount=Decimal("1000.00"),
            restocking_fee=Decimal("100.00")
        )
        
        assert sales_return.net_refund_amount == Decimal("900.00")
    
    def test_net_refund_amount_no_fee(self):
        """Test net refund with no restocking fee"""
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Wrong item shipped",
            refund_amount=Decimal("750.00"),
            restocking_fee=Decimal("0.00")
        )
        
        assert sales_return.net_refund_amount == Decimal("750.00")
    
    def test_is_approved(self):
        """Test approval status check"""
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Product not as described",
            refund_amount=Decimal("200.00")
        )
        
        # Initially not approved
        assert sales_return.is_approved is False
        
        # After approval
        sales_return.approved_by_id = uuid4()
        assert sales_return.is_approved is True
    
    def test_approve(self):
        """Test return approval"""
        approver_id = uuid4()
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Damaged in shipping",
            refund_amount=Decimal("300.00")
        )
        
        # Approve the return
        sales_return.approve(approver_id)
        assert sales_return.approved_by_id == approver_id
        assert sales_return.is_approved is True
        
        # Try to approve already approved return
        with pytest.raises(ValueError, match="Return has already been approved"):
            sales_return.approve(uuid4())
    
    def test_return_with_high_restocking_fee(self):
        """Test return with high restocking fee"""
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Customer changed mind after opening",
            refund_amount=Decimal("500.00"),
            restocking_fee=Decimal("125.00")  # 25% restocking fee
        )
        
        assert sales_return.net_refund_amount == Decimal("375.00")
    
    def test_return_with_return_id(self):
        """Test return with custom return ID"""
        sales_return = SalesReturn(
            return_id="RET-2024-001",
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Defective unit",
            refund_amount=Decimal("800.00")
        )
        
        assert sales_return.return_id == "RET-2024-001"
    
    def test_return_reason_required(self):
        """Test that reason is stored properly"""
        long_reason = "Product arrived damaged. Box was crushed and item inside was broken. " \
                     "Customer provided photos of the damage. Approved for full refund."
        
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason=long_reason,
            refund_amount=Decimal("1500.00")
        )
        
        assert sales_return.reason == long_reason
    
    def test_zero_refund_amount(self):
        """Test return with zero refund (exchange only)"""
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Exchange for different size",
            refund_amount=Decimal("0.00"),
            restocking_fee=Decimal("0.00")
        )
        
        assert sales_return.refund_amount == Decimal("0.00")
        assert sales_return.net_refund_amount == Decimal("0.00")
    
    def test_partial_return(self):
        """Test partial return scenario"""
        # Return of 2 items from a 5 item order
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Only returning 2 defective items from the order",
            refund_amount=Decimal("400.00"),  # 2 items @ $200 each
            restocking_fee=Decimal("0.00")    # No fee for defective items
        )
        
        assert sales_return.refund_amount == Decimal("400.00")
        assert sales_return.net_refund_amount == Decimal("400.00")
    
    def test_restocking_fee_exceeds_refund(self):
        """Test when restocking fee exceeds refund amount"""
        # This is an edge case that should be prevented at use case level
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Excessive damage caused by customer",
            refund_amount=Decimal("100.00"),
            restocking_fee=Decimal("150.00")
        )
        
        # Net refund would be negative
        assert sales_return.net_refund_amount == Decimal("-50.00")
    
    def test_return_timestamps(self):
        """Test return date handling"""
        return_date = datetime(2024, 1, 15, 10, 30, 0)
        
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=return_date,
            reason="Wrong color",
            refund_amount=Decimal("250.00")
        )
        
        assert sales_return.return_date == return_date
    
    def test_update_return_details(self):
        """Test updating return details before approval"""
        sales_return = SalesReturn(
            sales_transaction_id=uuid4(),
            return_date=datetime.now(),
            reason="Initial reason",
            refund_amount=Decimal("300.00"),
            restocking_fee=Decimal("30.00")
        )
        
        # Update details
        sales_return.reason = "Updated reason with more details"
        sales_return.refund_amount = Decimal("350.00")
        sales_return.restocking_fee = Decimal("35.00")
        
        assert sales_return.reason == "Updated reason with more details"
        assert sales_return.refund_amount == Decimal("350.00")
        assert sales_return.restocking_fee == Decimal("35.00")
        assert sales_return.net_refund_amount == Decimal("315.00")