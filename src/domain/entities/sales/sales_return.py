"""Sales Return Entity

This module defines the SalesReturn entity which represents product returns
for sales transactions.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.domain.entities.base_entity import BaseEntity


class SalesReturn(BaseEntity):
    """
    Represents a sales return in the system.
    
    This entity captures information about products being returned including
    the reason, refund amount, and approval details.
    """
    
    def __init__(
        self,
        sales_transaction_id: str,
        return_date: datetime,
        reason: str,
        refund_amount: Decimal = Decimal("0"),
        restocking_fee: Decimal = Decimal("0"),
        return_id: Optional[str] = None,
        approved_by_id: Optional[str] = None,
        **kwargs
    ):
        """Initialize a sales return."""
        super().__init__(**kwargs)
        self.return_id = return_id
        self.sales_transaction_id = sales_transaction_id
        self.return_date = return_date
        self.reason = reason
        self.approved_by_id = approved_by_id
        self.refund_amount = refund_amount
        self.restocking_fee = restocking_fee
    
    @property
    def net_refund_amount(self) -> Decimal:
        """
        Calculate the net refund amount after restocking fee.
        
        Returns:
            The net refund amount
        """
        return self.refund_amount - self.restocking_fee
    
    @property
    def is_approved(self) -> bool:
        """Check if the return has been approved."""
        return self.approved_by_id is not None
    
    def approve(self, approved_by_id: str) -> None:
        """
        Approve the return.
        
        Args:
            approved_by_id: The ID of the user approving the return
        """
        if self.is_approved:
            raise ValueError("Return has already been approved")
        
        self.approved_by_id = approved_by_id
    
    def calculate_refund(self, total_item_value: Decimal) -> None:
        """
        Calculate the refund amount based on returned items.
        
        Args:
            total_item_value: The total value of items being returned
        """
        if total_item_value < Decimal("0"):
            raise ValueError("Total item value cannot be negative")
        
        self.refund_amount = total_item_value
    
    def apply_restocking_fee(self, fee_percentage: Decimal) -> None:
        """
        Apply a restocking fee as a percentage of the refund amount.
        
        Args:
            fee_percentage: The restocking fee percentage (0-100)
            
        Raises:
            ValueError: If the fee percentage is invalid
        """
        if not Decimal("0") <= fee_percentage <= Decimal("100"):
            raise ValueError("Restocking fee percentage must be between 0 and 100")
        
        self.restocking_fee = self.refund_amount * (fee_percentage / Decimal("100"))
    
    def validate_return(self) -> None:
        """
        Validate the return details.
        
        Raises:
            ValueError: If the return is invalid
        """
        if not self.reason or not self.reason.strip():
            raise ValueError("Return reason is required")
        
        if self.refund_amount < Decimal("0"):
            raise ValueError("Refund amount cannot be negative")
        
        if self.restocking_fee < Decimal("0"):
            raise ValueError("Restocking fee cannot be negative")
        
        if self.restocking_fee > self.refund_amount:
            raise ValueError("Restocking fee cannot exceed refund amount")
    
    def __repr__(self) -> str:
        """Return string representation of the sales return."""
        return (
            f"SalesReturn(id={self.id}, return_id={self.return_id}, "
            f"sales_transaction_id={self.sales_transaction_id}, "
            f"refund_amount={self.refund_amount})"
        )