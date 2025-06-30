"""Payment Terms Value Object

This module defines the PaymentTerms enum representing the various payment
term options for sales transactions.
"""

from enum import Enum


class PaymentTerms(str, Enum):
    """
    Enumeration of available payment terms for sales transactions.
    
    Payment terms define when payment is due for a sales order.
    """
    
    IMMEDIATE = "IMMEDIATE"
    """Payment due immediately upon order"""
    
    NET_15 = "NET_15"
    """Payment due within 15 days"""
    
    NET_30 = "NET_30"
    """Payment due within 30 days"""
    
    NET_45 = "NET_45"
    """Payment due within 45 days"""
    
    NET_60 = "NET_60"
    """Payment due within 60 days"""
    
    NET_90 = "NET_90"
    """Payment due within 90 days"""
    
    COD = "COD"
    """Cash on delivery"""
    
    PREPAID = "PREPAID"
    """Payment required before order processing"""
    
    @classmethod
    def credit_terms(cls) -> list['PaymentTerms']:
        """Get list of terms that extend credit to customer."""
        return [cls.NET_15, cls.NET_30, cls.NET_45, cls.NET_60, cls.NET_90]
    
    @classmethod
    def immediate_payment_terms(cls) -> list['PaymentTerms']:
        """Get list of terms requiring immediate payment."""
        return [cls.IMMEDIATE, cls.COD, cls.PREPAID]
    
    def get_days(self) -> int:
        """
        Get the number of days for the payment term.
        
        Returns:
            Number of days until payment is due
        """
        days_mapping = {
            self.IMMEDIATE: 0,
            self.NET_15: 15,
            self.NET_30: 30,
            self.NET_45: 45,
            self.NET_60: 60,
            self.NET_90: 90,
            self.COD: 0,
            self.PREPAID: 0
        }
        return days_mapping.get(self, 0)
    
    def requires_credit_check(self) -> bool:
        """Check if the payment term requires credit validation."""
        return self in self.credit_terms()
    
    def is_prepayment_required(self) -> bool:
        """Check if payment is required before order processing."""
        return self == self.PREPAID