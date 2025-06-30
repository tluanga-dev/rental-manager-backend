"""Sales Transaction Entity

This module defines the SalesTransaction entity which represents a sales order
in the system. It handles the core business logic related to sales transactions.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from src.domain.entities.base_entity import BaseEntity
from src.domain.value_objects.sales.sales_status import SalesStatus
from src.domain.value_objects.sales.payment_status import PaymentStatus
from src.domain.value_objects.sales.payment_terms import PaymentTerms


class SalesTransaction(BaseEntity):
    """
    Represents a sales transaction (order) in the system.
    
    This entity captures all information related to a sales order including
    customer details, items, pricing, payment, and delivery information.
    """
    
    def __init__(
        self,
        customer_id: UUID,
        order_date: datetime,
        status: SalesStatus = SalesStatus.DRAFT,
        payment_status: PaymentStatus = PaymentStatus.PENDING,
        payment_terms: PaymentTerms = PaymentTerms.IMMEDIATE,
        subtotal: Decimal = Decimal("0"),
        discount_amount: Decimal = Decimal("0"),
        tax_amount: Decimal = Decimal("0"),
        shipping_amount: Decimal = Decimal("0"),
        grand_total: Decimal = Decimal("0"),
        amount_paid: Decimal = Decimal("0"),
        transaction_id: Optional[str] = None,
        invoice_number: Optional[str] = None,
        delivery_date: Optional[datetime] = None,
        payment_due_date: Optional[datetime] = None,
        shipping_address: Optional[str] = None,
        billing_address: Optional[str] = None,
        purchase_order_number: Optional[str] = None,
        sales_person_id: Optional[UUID] = None,
        notes: Optional[str] = None,
        customer_notes: Optional[str] = None,
        **kwargs
    ):
        """Initialize a sales transaction."""
        super().__init__(**kwargs)
        self.transaction_id = transaction_id
        self.invoice_number = invoice_number
        self.customer_id = customer_id
        self.order_date = order_date
        self.delivery_date = delivery_date
        self.status = status
        self.payment_status = payment_status
        self.payment_terms = payment_terms
        self.payment_due_date = payment_due_date
        self.subtotal = subtotal
        self.discount_amount = discount_amount
        self.tax_amount = tax_amount
        self.shipping_amount = shipping_amount
        self.grand_total = grand_total
        self.amount_paid = amount_paid
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.purchase_order_number = purchase_order_number
        self.sales_person_id = sales_person_id
        self.notes = notes
        self.customer_notes = customer_notes
        
        # Calculate payment due date if not provided
        if not self.payment_due_date:
            self.calculate_payment_due_date()
    
    @property
    def balance_due(self) -> Decimal:
        """Calculate the remaining balance due."""
        return self.grand_total - self.amount_paid
    
    @property
    def is_overdue(self) -> bool:
        """Check if the payment is overdue."""
        if (self.payment_due_date and 
            self.payment_status not in [PaymentStatus.PAID, PaymentStatus.REFUNDED]):
            return datetime.now() > self.payment_due_date
        return False
    
    @property
    def days_overdue(self) -> int:
        """Calculate the number of days overdue."""
        if self.is_overdue and self.payment_due_date:
            delta = datetime.now() - self.payment_due_date
            return delta.days
        return 0
    
    @property
    def is_fully_paid(self) -> bool:
        """Check if the transaction is fully paid."""
        return self.amount_paid >= self.grand_total
    
    def calculate_payment_due_date(self) -> None:
        """Calculate the payment due date based on payment terms."""
        if not self.order_date:
            return
            
        terms_to_days = {
            PaymentTerms.IMMEDIATE: 0,
            PaymentTerms.NET_15: 15,
            PaymentTerms.NET_30: 30,
            PaymentTerms.NET_45: 45,
            PaymentTerms.NET_60: 60,
            PaymentTerms.NET_90: 90,
            PaymentTerms.COD: 0,
            PaymentTerms.PREPAID: 0,
        }
        
        days = terms_to_days.get(self.payment_terms, 0)
        self.payment_due_date = self.order_date + timedelta(days=days)
    
    def update_payment(self, amount: Decimal, notes: Optional[str] = None) -> None:
        """
        Update the payment amount and status.
        
        Args:
            amount: The new total amount paid
            notes: Optional payment notes
        """
        if amount < Decimal("0"):
            raise ValueError("Payment amount cannot be negative")
        
        self.amount_paid = amount
        
        # Update payment status based on amount
        if self.amount_paid >= self.grand_total:
            self.payment_status = PaymentStatus.PAID
        elif self.amount_paid > Decimal("0"):
            self.payment_status = PaymentStatus.PARTIAL
        else:
            self.payment_status = PaymentStatus.PENDING
            
        # Check if overdue
        if self.is_overdue and self.payment_status not in [PaymentStatus.PAID, PaymentStatus.REFUNDED]:
            self.payment_status = PaymentStatus.OVERDUE
        
        # Add payment notes if provided
        if notes:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payment_note = f"[{timestamp}] Payment Update: {notes}"
            if self.notes:
                self.notes = f"{self.notes}\n{payment_note}"
            else:
                self.notes = payment_note
    
    def confirm_order(self) -> None:
        """
        Confirm a draft order.
        
        Raises:
            ValueError: If the order is not in DRAFT status
        """
        if self.status != SalesStatus.DRAFT:
            raise ValueError(f"Cannot confirm order with status: {self.status}")
        
        self.status = SalesStatus.CONFIRMED
    
    def cancel_order(self) -> None:
        """
        Cancel an order.
        
        Raises:
            ValueError: If the order is already shipped or delivered
        """
        if self.status in [SalesStatus.SHIPPED, SalesStatus.DELIVERED]:
            raise ValueError("Cannot cancel shipped or delivered orders")
        
        self.status = SalesStatus.CANCELLED
        
        # Update payment status if needed
        if self.amount_paid > Decimal("0"):
            self.payment_status = PaymentStatus.REFUNDED
    
    def mark_as_shipped(self) -> None:
        """Mark the order as shipped."""
        if self.status not in [SalesStatus.CONFIRMED, SalesStatus.PROCESSING]:
            raise ValueError(f"Cannot ship order with status: {self.status}")
        
        self.status = SalesStatus.SHIPPED
    
    def mark_as_delivered(self, delivery_date: Optional[datetime] = None) -> None:
        """
        Mark the order as delivered.
        
        Args:
            delivery_date: The actual delivery date (defaults to now)
        """
        if self.status != SalesStatus.SHIPPED:
            raise ValueError("Order must be shipped before marking as delivered")
        
        self.status = SalesStatus.DELIVERED
        self.delivery_date = delivery_date or datetime.now()
    
    def calculate_totals(
        self, 
        subtotal: Decimal, 
        tax_amount: Decimal, 
        discount_amount: Decimal
    ) -> None:
        """
        Calculate and update the transaction totals.
        
        Args:
            subtotal: The subtotal of all items
            tax_amount: The total tax amount
            discount_amount: The total discount amount
        """
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount
        
        # Calculate grand total
        self.grand_total = (
            self.subtotal - self.discount_amount + 
            self.tax_amount + self.shipping_amount
        )
    
    def can_process_return(self) -> bool:
        """Check if the transaction can have returns processed."""
        return self.status in [SalesStatus.DELIVERED, SalesStatus.SHIPPED]
    
    def __repr__(self) -> str:
        """Return string representation of the sales transaction."""
        return (
            f"SalesTransaction(id={self.id}, transaction_id={self.transaction_id}, "
            f"customer_id={self.customer_id}, status={self.status}, "
            f"grand_total={self.grand_total})"
        )