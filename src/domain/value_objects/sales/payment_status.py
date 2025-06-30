"""Payment Status Value Object

This module defines the PaymentStatus enum representing the various payment
states for a sales transaction.
"""

from enum import Enum


class PaymentStatus(str, Enum):
    """
    Enumeration of possible payment statuses for a sales transaction.
    
    The payment status tracks the current state of payment collection
    for a sales order.
    """
    
    PENDING = "PENDING"
    """No payment has been received yet"""
    
    PARTIAL = "PARTIAL"
    """Partial payment has been received"""
    
    PAID = "PAID"
    """Full payment has been received"""
    
    OVERDUE = "OVERDUE"
    """Payment is past the due date"""
    
    REFUNDED = "REFUNDED"
    """Payment has been refunded"""
    
    @classmethod
    def unpaid_statuses(cls) -> list['PaymentStatus']:
        """Get list of statuses indicating unpaid or partially paid orders."""
        return [cls.PENDING, cls.PARTIAL, cls.OVERDUE]
    
    @classmethod
    def paid_statuses(cls) -> list['PaymentStatus']:
        """Get list of statuses indicating fully paid orders."""
        return [cls.PAID, cls.REFUNDED]
    
    @classmethod
    def requires_action_statuses(cls) -> list['PaymentStatus']:
        """Get list of statuses that require payment action."""
        return [cls.PENDING, cls.PARTIAL, cls.OVERDUE]
    
    def is_fully_paid(self) -> bool:
        """Check if the status indicates full payment."""
        return self in [self.PAID, self.REFUNDED]
    
    def can_accept_payment(self) -> bool:
        """Check if the status allows accepting more payment."""
        return self in [self.PENDING, self.PARTIAL, self.OVERDUE]