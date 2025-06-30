"""Tests for Sales value objects (enums)"""

import pytest

from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms


class TestSalesStatus:
    """Test suite for SalesStatus enum"""
    
    def test_sales_status_values(self):
        """Test all sales status values exist"""
        assert SalesStatus.DRAFT == "DRAFT"
        assert SalesStatus.CONFIRMED == "CONFIRMED"
        assert SalesStatus.PROCESSING == "PROCESSING"
        assert SalesStatus.SHIPPED == "SHIPPED"
        assert SalesStatus.DELIVERED == "DELIVERED"
        assert SalesStatus.CANCELLED == "CANCELLED"
    
    def test_can_transition_to_valid_transitions(self):
        """Test valid status transitions"""
        # DRAFT can transition to CONFIRMED or CANCELLED
        assert SalesStatus.DRAFT.can_transition_to(SalesStatus.CONFIRMED) is True
        assert SalesStatus.DRAFT.can_transition_to(SalesStatus.CANCELLED) is True
        assert SalesStatus.DRAFT.can_transition_to(SalesStatus.PROCESSING) is False
        
        # CONFIRMED can transition to PROCESSING or CANCELLED
        assert SalesStatus.CONFIRMED.can_transition_to(SalesStatus.PROCESSING) is True
        assert SalesStatus.CONFIRMED.can_transition_to(SalesStatus.CANCELLED) is True
        assert SalesStatus.CONFIRMED.can_transition_to(SalesStatus.SHIPPED) is False
        
        # PROCESSING can transition to SHIPPED or CANCELLED (based on implementation)
        assert SalesStatus.PROCESSING.can_transition_to(SalesStatus.SHIPPED) is True
        assert SalesStatus.PROCESSING.can_transition_to(SalesStatus.CANCELLED) is True
        assert SalesStatus.PROCESSING.can_transition_to(SalesStatus.DELIVERED) is False
        
        # SHIPPED can only transition to DELIVERED
        assert SalesStatus.SHIPPED.can_transition_to(SalesStatus.DELIVERED) is True
        assert SalesStatus.SHIPPED.can_transition_to(SalesStatus.CANCELLED) is False
        
        # DELIVERED is final state
        assert SalesStatus.DELIVERED.can_transition_to(SalesStatus.DRAFT) is False
        assert SalesStatus.DELIVERED.can_transition_to(SalesStatus.CANCELLED) is False
        
        # CANCELLED is final state
        assert SalesStatus.CANCELLED.can_transition_to(SalesStatus.DRAFT) is False
        assert SalesStatus.CANCELLED.can_transition_to(SalesStatus.CONFIRMED) is False
    
    def test_all_statuses_have_transition_rules(self):
        """Test that all statuses can check transitions"""
        for status in SalesStatus:
            # All statuses should be able to check transitions
            # Test a few transition attempts
            assert isinstance(status.can_transition_to(SalesStatus.CONFIRMED), bool)
            assert isinstance(status.can_transition_to(SalesStatus.CANCELLED), bool)


class TestPaymentStatus:
    """Test suite for PaymentStatus enum"""
    
    def test_payment_status_values(self):
        """Test all payment status values exist"""
        assert PaymentStatus.PENDING == "PENDING"
        assert PaymentStatus.PARTIAL == "PARTIAL"
        assert PaymentStatus.PAID == "PAID"
        assert PaymentStatus.OVERDUE == "OVERDUE"
        assert PaymentStatus.REFUNDED == "REFUNDED"
    
    def test_payment_status_methods(self):
        """Test payment status utility methods"""
        # Test is_fully_paid
        assert PaymentStatus.PAID.is_fully_paid() is True
        assert PaymentStatus.REFUNDED.is_fully_paid() is True
        assert PaymentStatus.PENDING.is_fully_paid() is False
        assert PaymentStatus.PARTIAL.is_fully_paid() is False
        assert PaymentStatus.OVERDUE.is_fully_paid() is False
        
        # Test can_accept_payment
        assert PaymentStatus.PENDING.can_accept_payment() is True
        assert PaymentStatus.PARTIAL.can_accept_payment() is True
        assert PaymentStatus.OVERDUE.can_accept_payment() is True
        assert PaymentStatus.PAID.can_accept_payment() is False
        assert PaymentStatus.REFUNDED.can_accept_payment() is False
    
    def test_payment_status_class_methods(self):
        """Test payment status class methods"""
        unpaid = PaymentStatus.unpaid_statuses()
        assert PaymentStatus.PENDING in unpaid
        assert PaymentStatus.PARTIAL in unpaid
        assert PaymentStatus.OVERDUE in unpaid
        assert PaymentStatus.PAID not in unpaid
        
        paid = PaymentStatus.paid_statuses()
        assert PaymentStatus.PAID in paid
        assert PaymentStatus.REFUNDED in paid
        assert PaymentStatus.PENDING not in paid


class TestPaymentTerms:
    """Test suite for PaymentTerms enum"""
    
    def test_payment_terms_values(self):
        """Test all payment terms values exist"""
        assert PaymentTerms.IMMEDIATE == "IMMEDIATE"
        assert PaymentTerms.NET_15 == "NET_15"
        assert PaymentTerms.NET_30 == "NET_30"
        assert PaymentTerms.NET_45 == "NET_45"
        assert PaymentTerms.NET_60 == "NET_60"
        assert PaymentTerms.NET_90 == "NET_90"
        assert PaymentTerms.COD == "COD"
        assert PaymentTerms.PREPAID == "PREPAID"
    
    def test_get_days(self):
        """Test getting days for each payment term"""
        assert PaymentTerms.IMMEDIATE.get_days() == 0
        assert PaymentTerms.NET_15.get_days() == 15
        assert PaymentTerms.NET_30.get_days() == 30
        assert PaymentTerms.NET_45.get_days() == 45
        assert PaymentTerms.NET_60.get_days() == 60
        assert PaymentTerms.NET_90.get_days() == 90
        assert PaymentTerms.COD.get_days() == 0
        assert PaymentTerms.PREPAID.get_days() == 0
    
    def test_all_payment_terms_have_days_mapping(self):
        """Test that all payment terms have defined days mapping"""
        for term in PaymentTerms:
            days = term.get_days()
            assert days is not None
            assert isinstance(days, int)
            assert days >= 0
    
    def test_payment_terms_string_representation(self):
        """Test string representation of payment terms"""
        # Enums inherit from str, so value should be the string value
        assert PaymentTerms.NET_30.value == "NET_30"
        assert PaymentTerms.NET_30 == "NET_30"  # Direct comparison
    
    def test_payment_terms_comparison(self):
        """Test payment terms can be compared"""
        assert PaymentTerms.NET_30 == PaymentTerms.NET_30
        assert PaymentTerms.NET_30 != PaymentTerms.NET_60
        
        # Test that different terms with same days are still different
        assert PaymentTerms.IMMEDIATE != PaymentTerms.COD
        assert PaymentTerms.IMMEDIATE.get_days() == PaymentTerms.COD.get_days()