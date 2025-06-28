from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from enum import Enum

from .base_entity import BaseEntity


class WarrantyPeriodType(Enum):
    DAYS = "DAYS"
    MONTHS = "MONTHS"
    YEARS = "YEARS"


class PurchaseOrderLineItem(BaseEntity):
    def __init__(
        self,
        purchase_order_id: UUID,
        inventory_item_master_id: UUID,
        warehouse_id: UUID,
        quantity: int,
        unit_price: Decimal,
        serial_number: Optional[str] = None,
        discount: Decimal = Decimal("0.00"),
        tax_amount: Decimal = Decimal("0.00"),
        received_quantity: int = 0,
        reference_number: Optional[str] = None,
        warranty_period_type: Optional[WarrantyPeriodType] = None,
        warranty_period: Optional[int] = None,
        rental_rate: Decimal = Decimal("0.00"),
        replacement_cost: Decimal = Decimal("0.00"),
        late_fee_rate: Decimal = Decimal("0.00"),
        sell_tax_rate: int = 0,
        rent_tax_rate: int = 0,
        rentable: bool = True,
        sellable: bool = False,
        selling_price: Decimal = Decimal("0.00"),
        line_item_id: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        created_by: Optional[str] = None,
        is_active: bool = True,
    ) -> None:
        super().__init__(line_item_id, created_at, updated_at, created_by, is_active)
        self._purchase_order_id = purchase_order_id
        self._inventory_item_master_id = inventory_item_master_id
        self._warehouse_id = warehouse_id
        self._quantity = self._validate_quantity(quantity)
        self._unit_price = self._validate_amount(unit_price)
        self._serial_number = serial_number
        self._discount = self._validate_amount(discount)
        self._tax_amount = self._validate_amount(tax_amount)
        self._received_quantity = self._validate_quantity(received_quantity, allow_zero=True)
        self._reference_number = reference_number
        self._warranty_period_type = warranty_period_type
        self._warranty_period = self._validate_warranty_period(warranty_period, warranty_period_type)
        self._rental_rate = self._validate_amount(rental_rate)
        self._replacement_cost = self._validate_amount(replacement_cost)
        self._late_fee_rate = self._validate_amount(late_fee_rate)
        self._sell_tax_rate = self._validate_tax_rate(sell_tax_rate)
        self._rent_tax_rate = self._validate_tax_rate(rent_tax_rate)
        self._rentable = rentable
        self._sellable = sellable
        self._selling_price = self._validate_amount(selling_price)

    @property
    def purchase_order_id(self) -> UUID:
        return self._purchase_order_id

    @property
    def inventory_item_master_id(self) -> UUID:
        return self._inventory_item_master_id

    @property
    def warehouse_id(self) -> UUID:
        return self._warehouse_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def unit_price(self) -> Decimal:
        return self._unit_price

    @property
    def serial_number(self) -> Optional[str]:
        return self._serial_number

    @property
    def discount(self) -> Decimal:
        return self._discount

    @property
    def tax_amount(self) -> Decimal:
        return self._tax_amount

    @property
    def amount(self) -> Decimal:
        """Calculate the line amount before tax."""
        return (self._unit_price * self._quantity) - self._discount

    @property
    def total_price(self) -> Decimal:
        """Calculate the total price including tax."""
        return self.amount + self._tax_amount

    @property
    def received_quantity(self) -> int:
        return self._received_quantity

    @property
    def reference_number(self) -> Optional[str]:
        return self._reference_number

    @property
    def warranty_period_type(self) -> Optional[WarrantyPeriodType]:
        return self._warranty_period_type

    @property
    def warranty_period(self) -> Optional[int]:
        return self._warranty_period

    @property
    def rental_rate(self) -> Decimal:
        return self._rental_rate

    @property
    def replacement_cost(self) -> Decimal:
        return self._replacement_cost

    @property
    def late_fee_rate(self) -> Decimal:
        return self._late_fee_rate

    @property
    def sell_tax_rate(self) -> int:
        return self._sell_tax_rate

    @property
    def rent_tax_rate(self) -> int:
        return self._rent_tax_rate

    @property
    def rentable(self) -> bool:
        return self._rentable

    @property
    def sellable(self) -> bool:
        return self._sellable

    @property
    def selling_price(self) -> Decimal:
        return self._selling_price

    def update_quantity(self, quantity: int) -> None:
        """Update the ordered quantity."""
        self._quantity = self._validate_quantity(quantity)
        self._touch_updated_at()

    def update_pricing(
        self,
        unit_price: Optional[Decimal] = None,
        discount: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None,
    ) -> None:
        """Update pricing information."""
        if unit_price is not None:
            self._unit_price = self._validate_amount(unit_price)
        if discount is not None:
            self._discount = self._validate_amount(discount)
        if tax_amount is not None:
            self._tax_amount = self._validate_amount(tax_amount)
        self._touch_updated_at()

    def receive_items(self, quantity: int) -> None:
        """Record receipt of items."""
        if quantity <= 0:
            raise ValueError("Received quantity must be positive")
        
        new_received_quantity = self._received_quantity + quantity
        if new_received_quantity > self._quantity:
            raise ValueError(
                f"Total received quantity ({new_received_quantity}) cannot exceed "
                f"ordered quantity ({self._quantity})"
            )
        
        self._received_quantity = new_received_quantity
        self._touch_updated_at()

    def update_warranty(
        self,
        warranty_period_type: Optional[WarrantyPeriodType] = None,
        warranty_period: Optional[int] = None,
    ) -> None:
        """Update warranty information."""
        if warranty_period_type is not None or warranty_period is not None:
            self._warranty_period = self._validate_warranty_period(
                warranty_period or self._warranty_period,
                warranty_period_type or self._warranty_period_type
            )
            if warranty_period_type is not None:
                self._warranty_period_type = warranty_period_type
            if warranty_period is not None:
                self._warranty_period = warranty_period
        self._touch_updated_at()

    def update_rental_info(
        self,
        rental_rate: Optional[Decimal] = None,
        replacement_cost: Optional[Decimal] = None,
        late_fee_rate: Optional[Decimal] = None,
        rent_tax_rate: Optional[int] = None,
        rentable: Optional[bool] = None,
    ) -> None:
        """Update rental-related information."""
        if rental_rate is not None:
            self._rental_rate = self._validate_amount(rental_rate)
        if replacement_cost is not None:
            self._replacement_cost = self._validate_amount(replacement_cost)
        if late_fee_rate is not None:
            self._late_fee_rate = self._validate_amount(late_fee_rate)
        if rent_tax_rate is not None:
            self._rent_tax_rate = self._validate_tax_rate(rent_tax_rate)
        if rentable is not None:
            self._rentable = rentable
        self._touch_updated_at()

    def update_selling_info(
        self,
        selling_price: Optional[Decimal] = None,
        sell_tax_rate: Optional[int] = None,
        sellable: Optional[bool] = None,
    ) -> None:
        """Update selling-related information."""
        if selling_price is not None:
            self._selling_price = self._validate_amount(selling_price)
        if sell_tax_rate is not None:
            self._sell_tax_rate = self._validate_tax_rate(sell_tax_rate)
        if sellable is not None:
            self._sellable = sellable
        self._touch_updated_at()

    def is_fully_received(self) -> bool:
        """Check if all ordered items have been received."""
        return self._received_quantity >= self._quantity

    def is_partially_received(self) -> bool:
        """Check if some items have been received."""
        return 0 < self._received_quantity < self._quantity

    def get_remaining_quantity(self) -> int:
        """Get the quantity yet to be received."""
        return max(0, self._quantity - self._received_quantity)

    def get_display_info(self) -> dict:
        """Get line item information for display purposes."""
        return {
            "id": str(self.id),
            "inventory_item_master_id": str(self.inventory_item_master_id),
            "warehouse_id": str(self.warehouse_id),
            "quantity": self.quantity,
            "received_quantity": self.received_quantity,
            "unit_price": str(self.unit_price),
            "total_price": str(self.total_price),
            "serial_number": self.serial_number,
            "is_fully_received": self.is_fully_received(),
        }

    @staticmethod
    def _validate_quantity(quantity: int, allow_zero: bool = False) -> int:
        """Validate quantity."""
        if not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer")
        
        if allow_zero:
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
        else:
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
        
        return quantity

    @staticmethod
    def _validate_amount(amount: Decimal) -> Decimal:
        """Validate amount is non-negative."""
        if amount < 0:
            raise ValueError("Amount cannot be negative")
        return amount

    @staticmethod
    def _validate_tax_rate(rate: int) -> int:
        """Validate tax rate."""
        if not isinstance(rate, int):
            raise ValueError("Tax rate must be an integer")
        
        if rate < 0 or rate > 100:
            raise ValueError("Tax rate must be between 0 and 100")
        
        return rate

    @staticmethod
    def _validate_warranty_period(
        period: Optional[int], 
        period_type: Optional[WarrantyPeriodType]
    ) -> Optional[int]:
        """Validate warranty period."""
        if period is None:
            return None
        
        if period_type is None:
            raise ValueError("Warranty period type is required when warranty period is specified")
        
        if not isinstance(period, int) or period <= 0:
            raise ValueError("Warranty period must be a positive integer")
        
        return period

    def __str__(self) -> str:
        return f"LineItem for PO {self.purchase_order_id} - Qty: {self.quantity}"

    def __repr__(self) -> str:
        return (
            f"PurchaseOrderLineItem(id={self.id}, purchase_order_id={self.purchase_order_id}, "
            f"item_id={self.inventory_item_master_id}, quantity={self.quantity})"
        )