from typing import Optional
from uuid import UUID
from datetime import datetime, date
from enum import Enum
from decimal import Decimal

from .base_entity import BaseEntity


class PurchaseOrderStatus(Enum):
    DRAFT = "DRAFT"
    ORDERED = "ORDERED"
    PARTIAL_RECEIVED = "PARTIAL_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class PurchaseOrder(BaseEntity):
    def __init__(
        self,
        order_number: str,
        vendor_id: UUID,
        order_date: date,
        expected_delivery_date: Optional[date] = None,
        status: PurchaseOrderStatus = PurchaseOrderStatus.DRAFT,
        total_amount: Decimal = Decimal("0.00"),
        total_tax_amount: Decimal = Decimal("0.00"),
        total_discount: Decimal = Decimal("0.00"),
        grand_total: Decimal = Decimal("0.00"),
        reference_number: Optional[str] = None,
        invoice_number: Optional[str] = None,
        notes: Optional[str] = None,
        purchase_order_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(purchase_order_id, created_at, updated_at, created_by, is_active)
        self._order_number = self._validate_order_number(order_number)
        self._vendor_id = vendor_id
        self._order_date = order_date
        self._expected_delivery_date = expected_delivery_date
        self._status = status
        self._total_amount = self._validate_amount(total_amount)
        self._total_tax_amount = self._validate_amount(total_tax_amount)
        self._total_discount = self._validate_amount(total_discount)
        self._grand_total = self._validate_amount(grand_total)
        self._reference_number = reference_number
        self._invoice_number = invoice_number
        self._notes = notes

    @property
    def order_number(self) -> str:
        return self._order_number

    @property
    def vendor_id(self) -> UUID:
        return self._vendor_id

    @property
    def order_date(self) -> date:
        return self._order_date

    @property
    def expected_delivery_date(self) -> Optional[date]:
        return self._expected_delivery_date

    @property
    def status(self) -> PurchaseOrderStatus:
        return self._status

    @property
    def total_amount(self) -> Decimal:
        return self._total_amount

    @property
    def total_tax_amount(self) -> Decimal:
        return self._total_tax_amount

    @property
    def total_discount(self) -> Decimal:
        return self._total_discount

    @property
    def grand_total(self) -> Decimal:
        return self._grand_total

    @property
    def reference_number(self) -> Optional[str]:
        return self._reference_number

    @property
    def invoice_number(self) -> Optional[str]:
        return self._invoice_number

    @property
    def notes(self) -> Optional[str]:
        return self._notes

    def update_dates(
        self,
        order_date: Optional[date] = None,
        expected_delivery_date: Optional[date] = None,
    ) -> None:
        """Update order dates."""
        if order_date is not None:
            self._order_date = order_date
        if expected_delivery_date is not None:
            self._expected_delivery_date = expected_delivery_date
        self._touch_updated_at()

    def update_references(
        self,
        reference_number: Optional[str] = None,
        invoice_number: Optional[str] = None,
    ) -> None:
        """Update reference numbers."""
        if reference_number is not None:
            self._reference_number = reference_number
        if invoice_number is not None:
            self._invoice_number = invoice_number
        self._touch_updated_at()

    def update_notes(self, notes: Optional[str]) -> None:
        """Update purchase order notes."""
        self._notes = notes
        self._touch_updated_at()

    def update_totals(
        self,
        total_amount: Decimal,
        total_tax_amount: Decimal,
        total_discount: Decimal,
    ) -> None:
        """Update purchase order totals and calculate grand total."""
        self._total_amount = self._validate_amount(total_amount)
        self._total_tax_amount = self._validate_amount(total_tax_amount)
        self._total_discount = self._validate_amount(total_discount)
        self._grand_total = self._total_amount + self._total_tax_amount - self._total_discount
        self._touch_updated_at()

    def change_status(self, new_status: PurchaseOrderStatus) -> None:
        """Change the status of the purchase order with validation."""
        if not self._is_valid_status_transition(self._status, new_status):
            raise ValueError(
                f"Invalid status transition from {self._status.value} to {new_status.value}"
            )
        
        self._status = new_status
        self._touch_updated_at()

    def mark_as_ordered(self) -> None:
        """Mark the purchase order as ordered."""
        self.change_status(PurchaseOrderStatus.ORDERED)

    def mark_as_partially_received(self) -> None:
        """Mark the purchase order as partially received."""
        self.change_status(PurchaseOrderStatus.PARTIAL_RECEIVED)

    def mark_as_received(self) -> None:
        """Mark the purchase order as fully received."""
        self.change_status(PurchaseOrderStatus.RECEIVED)

    def cancel(self) -> None:
        """Cancel the purchase order."""
        if self._status in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.CANCELLED]:
            raise ValueError(
                f"Cannot cancel purchase order with status {self._status.value}"
            )
        self.change_status(PurchaseOrderStatus.CANCELLED)

    def is_editable(self) -> bool:
        """Check if the purchase order can be edited."""
        return self._status in [PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.ORDERED]

    def is_receivable(self) -> bool:
        """Check if the purchase order can receive items."""
        return self._status in [
            PurchaseOrderStatus.ORDERED,
            PurchaseOrderStatus.PARTIAL_RECEIVED,
        ]

    def get_display_info(self) -> dict:
        """Get purchase order information for display purposes."""
        return {
            "id": str(self.id),
            "order_number": self.order_number,
            "vendor_id": str(self.vendor_id),
            "order_date": self.order_date.isoformat(),
            "expected_delivery_date": (
                self.expected_delivery_date.isoformat() 
                if self.expected_delivery_date 
                else None
            ),
            "status": self.status.value,
            "grand_total": str(self.grand_total),
            "is_active": self.is_active,
        }

    @staticmethod
    def _validate_order_number(order_number: str) -> str:
        """Validate order number."""
        if not order_number or not order_number.strip():
            raise ValueError("Order number cannot be empty")
        
        order_number = order_number.strip()
        if len(order_number) > 50:
            raise ValueError("Order number cannot exceed 50 characters")
        
        return order_number

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        """Validate amount is non-negative."""
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        return amount

    @staticmethod
    def _is_valid_status_transition(
        current_status: PurchaseOrderStatus, 
        new_status: PurchaseOrderStatus
    ) -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            PurchaseOrderStatus.DRAFT: [
                PurchaseOrderStatus.ORDERED,
                PurchaseOrderStatus.CANCELLED,
            ],
            PurchaseOrderStatus.ORDERED: [
                PurchaseOrderStatus.PARTIAL_RECEIVED,
                PurchaseOrderStatus.RECEIVED,
                PurchaseOrderStatus.CANCELLED,
            ],
            PurchaseOrderStatus.PARTIAL_RECEIVED: [
                PurchaseOrderStatus.RECEIVED,
                PurchaseOrderStatus.CANCELLED,
            ],
            PurchaseOrderStatus.RECEIVED: [],  # No transitions from RECEIVED
            PurchaseOrderStatus.CANCELLED: [],  # No transitions from CANCELLED
        }
        
        return new_status in valid_transitions.get(current_status, [])

    def __str__(self) -> str:
        return f"PO-{self.order_number}"

    def __repr__(self) -> str:
        return (
            f"PurchaseOrder(id={self.id}, order_number='{self.order_number}', "
            f"vendor_id={self.vendor_id}, status={self.status.value})"
        )