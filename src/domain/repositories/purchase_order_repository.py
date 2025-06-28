from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date

from ..entities.purchase_order import PurchaseOrder, PurchaseOrderStatus


class PurchaseOrderRepository(ABC):
    @abstractmethod
    async def save(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Save a purchase order entity to the database."""
        pass

    @abstractmethod
    async def find_by_id(self, purchase_order_id: UUID) -> Optional[PurchaseOrder]:
        """Find a purchase order by its ID."""
        pass

    @abstractmethod
    async def find_by_order_number(self, order_number: str) -> Optional[PurchaseOrder]:
        """Find a purchase order by its order number."""
        pass

    @abstractmethod
    async def find_by_vendor(self, vendor_id: UUID, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find purchase orders by vendor ID."""
        pass

    @abstractmethod
    async def find_by_status(self, status: PurchaseOrderStatus, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find purchase orders by status."""
        pass

    @abstractmethod
    async def find_by_date_range(self, start_date: date, end_date: date, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find purchase orders within a date range."""
        pass

    @abstractmethod
    async def find_by_reference_number(self, reference_number: str) -> List[PurchaseOrder]:
        """Find purchase orders by reference number."""
        pass

    @abstractmethod
    async def find_by_invoice_number(self, invoice_number: str) -> List[PurchaseOrder]:
        """Find purchase orders by invoice number."""
        pass

    @abstractmethod
    async def search_purchase_orders(self, query: str, search_fields: List[str] = None, limit: int = 10) -> List[PurchaseOrder]:
        """Search purchase orders across multiple fields."""
        pass

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[PurchaseOrder]:
        """Find all purchase orders with pagination."""
        pass

    @abstractmethod
    async def update(self, purchase_order: PurchaseOrder) -> PurchaseOrder:
        """Update an existing purchase order."""
        pass

    @abstractmethod
    async def delete(self, purchase_order_id: UUID) -> bool:
        """Delete a purchase order by ID (soft delete)."""
        pass

    @abstractmethod
    async def exists(self, purchase_order_id: UUID) -> bool:
        """Check if a purchase order exists by ID."""
        pass

    @abstractmethod
    async def exists_by_order_number(self, order_number: str) -> bool:
        """Check if a purchase order exists by order number."""
        pass

    @abstractmethod
    async def count_by_status(self, status: PurchaseOrderStatus) -> int:
        """Count purchase orders by status."""
        pass

    @abstractmethod
    async def get_next_order_number(self) -> str:
        """Generate the next purchase order number."""
        pass