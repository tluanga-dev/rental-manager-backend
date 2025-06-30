"""Purchase Transaction Entity

This module defines the PurchaseTransaction entity which represents a purchase
transaction in the system. It handles the core business logic related to 
purchasing items from vendors.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity
from src.domain.value_objects.purchase.purchase_status import PurchaseStatus


class PurchaseTransaction(BaseEntity):
    """
    Represents a purchase transaction in the system.
    
    This entity captures all information related to purchasing items from
    vendors, including transaction details, pricing, and vendor information.
    """
    
    def __init__(
        self,
        transaction_id: str,
        transaction_date: date,
        vendor_id: UUID,
        status: PurchaseStatus = PurchaseStatus.DRAFT,
        total_amount: Decimal = Decimal("0.00"),
        grand_total: Decimal = Decimal("0.00"),
        purchase_order_number: Optional[str] = None,
        remarks: Optional[str] = None,
        **kwargs
    ):
        """Initialize a purchase transaction."""
        super().__init__(**kwargs)
        self.transaction_id = self._validate_transaction_id(transaction_id)
        self.transaction_date = transaction_date
        self.vendor_id = vendor_id
        self.status = status
        self.total_amount = self._validate_amount(total_amount)
        self.grand_total = self._validate_amount(grand_total)
        self.purchase_order_number = purchase_order_number
        self.remarks = remarks
    
    @staticmethod
    def _validate_transaction_id(transaction_id: str) -> str:
        """Validate transaction ID format."""
        if not transaction_id or not transaction_id.strip():
            raise ValueError("Transaction ID cannot be empty")
        
        if len(transaction_id.strip()) > 255:
            raise ValueError("Transaction ID cannot exceed 255 characters")
        
        return transaction_id.strip()
    
    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        """Validate that amount is non-negative."""
        if amount < Decimal("0"):
            raise ValueError("Amount cannot be negative")
        return amount
    
    def confirm_transaction(self) -> None:
        """
        Confirm a draft transaction.
        
        Raises:
            ValueError: If the transaction is not in DRAFT status
        """
        if self.status != PurchaseStatus.DRAFT:
            raise ValueError(f"Cannot confirm transaction with status: {self.status}")
        
        self.status = PurchaseStatus.CONFIRMED
    
    def start_processing(self) -> None:
        """
        Start processing a confirmed transaction.
        
        Raises:
            ValueError: If the transaction is not confirmed
        """
        if self.status != PurchaseStatus.CONFIRMED:
            raise ValueError(f"Cannot start processing transaction with status: {self.status}")
        
        self.status = PurchaseStatus.PROCESSING
    
    def mark_as_received(self) -> None:
        """
        Mark the transaction as received.
        
        Raises:
            ValueError: If the transaction is not being processed
        """
        if self.status != PurchaseStatus.PROCESSING:
            raise ValueError(f"Cannot mark transaction as received with status: {self.status}")
        
        self.status = PurchaseStatus.RECEIVED
    
    def complete_transaction(self) -> None:
        """
        Complete a received transaction.
        
        Raises:
            ValueError: If the transaction has not been received
        """
        if self.status != PurchaseStatus.RECEIVED:
            raise ValueError(f"Cannot complete transaction with status: {self.status}")
        
        self.status = PurchaseStatus.COMPLETED
    
    def cancel_transaction(self) -> None:
        """
        Cancel a transaction.
        
        Raises:
            ValueError: If the transaction is already completed
        """
        if self.status == PurchaseStatus.COMPLETED:
            raise ValueError("Cannot cancel completed transactions")
        
        self.status = PurchaseStatus.CANCELLED
    
    def update_totals(self, total_amount: Decimal, grand_total: Decimal) -> None:
        """
        Update transaction totals.
        
        Args:
            total_amount: The new total amount
            grand_total: The new grand total
        """
        self.total_amount = self._validate_amount(total_amount)
        self.grand_total = self._validate_amount(grand_total)
    
    def is_editable(self) -> bool:
        """Check if the transaction can be edited."""
        return self.status in [PurchaseStatus.DRAFT, PurchaseStatus.CONFIRMED]
    
    def is_cancellable(self) -> bool:
        """Check if the transaction can be cancelled."""
        return self.status != PurchaseStatus.COMPLETED
    
    def can_add_items(self) -> bool:
        """Check if items can be added to this transaction."""
        return self.status in [PurchaseStatus.DRAFT, PurchaseStatus.CONFIRMED]
    
    @property
    def transaction_id_display(self) -> str:
        """Get a display-friendly transaction ID."""
        return self.transaction_id
    
    def __repr__(self) -> str:
        """Return string representation of the purchase transaction."""
        return (
            f"PurchaseTransaction(id={self.id}, transaction_id={self.transaction_id}, "
            f"vendor_id={self.vendor_id}, status={self.status}, "
            f"grand_total={self.grand_total})"
        )