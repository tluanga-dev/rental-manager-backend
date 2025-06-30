"""Sales Domain Entities

This module contains all domain entities related to sales operations.
"""

from .sales_transaction import SalesTransaction
from .sales_transaction_item import SalesTransactionItem
from .sales_return import SalesReturn
from .sales_return_item import SalesReturnItem

__all__ = [
    "SalesTransaction",
    "SalesTransactionItem",
    "SalesReturn",
    "SalesReturnItem",
]