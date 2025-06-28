from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.purchase_order_line_item import PurchaseOrderLineItem


class PurchaseOrderLineItemRepository(ABC):
    @abstractmethod
    async def save(self, line_item: PurchaseOrderLineItem) -> PurchaseOrderLineItem:
        """Save a purchase order line item to the database."""
        pass

    @abstractmethod
    async def save_many(self, line_items: List[PurchaseOrderLineItem]) -> List[PurchaseOrderLineItem]:
        """Save multiple purchase order line items."""
        pass

    @abstractmethod
    async def find_by_id(self, line_item_id: UUID) -> Optional[PurchaseOrderLineItem]:
        """Find a line item by its ID."""
        pass

    @abstractmethod
    async def find_by_purchase_order(self, purchase_order_id: UUID) -> List[PurchaseOrderLineItem]:
        """Find all line items for a purchase order."""
        pass

    @abstractmethod
    async def find_by_inventory_item(self, inventory_item_master_id: UUID) -> List[PurchaseOrderLineItem]:
        """Find all line items for an inventory item."""
        pass

    @abstractmethod
    async def find_by_warehouse(self, warehouse_id: UUID) -> List[PurchaseOrderLineItem]:
        """Find all line items for a warehouse."""
        pass

    @abstractmethod
    async def find_by_serial_number(self, serial_number: str) -> Optional[PurchaseOrderLineItem]:
        """Find a line item by serial number."""
        pass

    @abstractmethod
    async def find_unreceived_items(self, purchase_order_id: Optional[UUID] = None) -> List[PurchaseOrderLineItem]:
        """Find line items that haven't been fully received."""
        pass

    @abstractmethod
    async def find_partially_received_items(self, purchase_order_id: Optional[UUID] = None) -> List[PurchaseOrderLineItem]:
        """Find line items that have been partially received."""
        pass

    @abstractmethod
    async def update(self, line_item: PurchaseOrderLineItem) -> PurchaseOrderLineItem:
        """Update an existing line item."""
        pass

    @abstractmethod
    async def update_many(self, line_items: List[PurchaseOrderLineItem]) -> List[PurchaseOrderLineItem]:
        """Update multiple line items."""
        pass

    @abstractmethod
    async def delete(self, line_item_id: UUID) -> bool:
        """Delete a line item by ID."""
        pass

    @abstractmethod
    async def delete_by_purchase_order(self, purchase_order_id: UUID) -> int:
        """Delete all line items for a purchase order. Returns number of deleted items."""
        pass

    @abstractmethod
    async def exists(self, line_item_id: UUID) -> bool:
        """Check if a line item exists by ID."""
        pass

    @abstractmethod
    async def exists_by_serial_number(self, serial_number: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if a line item exists by serial number, optionally excluding a specific ID."""
        pass

    @abstractmethod
    async def count_by_purchase_order(self, purchase_order_id: UUID) -> int:
        """Count line items for a purchase order."""
        pass

    @abstractmethod
    async def sum_total_by_purchase_order(self, purchase_order_id: UUID) -> dict:
        """Calculate sum of amounts, tax, and discount for a purchase order."""
        pass