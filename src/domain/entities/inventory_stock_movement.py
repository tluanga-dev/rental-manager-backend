from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .base_entity import BaseEntity


@dataclass
class InventoryStockMovement(BaseEntity):
    inventory_item_id: str
    movement_type: str
    inventory_transaction_id: str
    quantity: int
    quantity_on_hand_before: int
    quantity_on_hand_after: int
    warehouse_from_id: Optional[str] = None
    warehouse_to_id: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._validate()

    def _validate(self):
        valid_movement_types = [
            "PURCHASE", "PURCHASE_RETURN", "SELL", "SELL_RETURN",
            "RENT", "RENT_RETURN", "RECONCILIATION", "INTER_WAREHOUSE_TRANSFER"
        ]
        
        if self.movement_type not in valid_movement_types:
            raise ValueError(f"Invalid movement type: {self.movement_type}")
        
        if not self.inventory_transaction_id or not self.inventory_transaction_id.strip():
            raise ValueError("Transaction ID is required")
        
        # Validate quantities match the movement
        expected_quantity_change = self.quantity_on_hand_after - self.quantity_on_hand_before
        if expected_quantity_change != self.quantity:
            raise ValueError("Quantity change does not match before/after quantities")
        
        # Validate warehouse fields for transfers
        if self.movement_type == "INTER_WAREHOUSE_TRANSFER":
            if not self.warehouse_from_id or not self.warehouse_to_id:
                raise ValueError("Both source and destination warehouses are required for transfers")
            if self.warehouse_from_id == self.warehouse_to_id:
                raise ValueError("Source and destination warehouses must be different")
        
        # Validate quantity signs based on movement type
        if self.movement_type in ["PURCHASE", "SELL_RETURN", "RENT_RETURN"]:
            if self.quantity < 0:
                raise ValueError(f"Quantity must be positive for {self.movement_type}")
        elif self.movement_type in ["SELL", "PURCHASE_RETURN", "RENT"]:
            if self.quantity > 0:
                raise ValueError(f"Quantity must be negative for {self.movement_type}")

    def is_inbound_movement(self) -> bool:
        """Check if this is an inbound movement (increasing stock)"""
        return self.movement_type in ["PURCHASE", "SELL_RETURN", "RENT_RETURN"]

    def is_outbound_movement(self) -> bool:
        """Check if this is an outbound movement (decreasing stock)"""
        return self.movement_type in ["SELL", "PURCHASE_RETURN", "RENT"]

    def is_transfer_movement(self) -> bool:
        """Check if this is a transfer movement"""
        return self.movement_type == "INTER_WAREHOUSE_TRANSFER"

    def is_reconciliation(self) -> bool:
        """Check if this is a reconciliation movement"""
        return self.movement_type == "RECONCILIATION"

    def get_absolute_quantity(self) -> int:
        """Get the absolute value of quantity moved"""
        return abs(self.quantity)