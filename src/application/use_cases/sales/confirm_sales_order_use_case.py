"""Confirm Sales Order Use Case

This module defines the use case for confirming a draft sales order.
"""

from typing import Optional

import logging

from src.domain.entities.sales import SalesTransaction
from src.domain.repositories.sales_transaction_repository import ISalesTransactionRepository
from src.domain.repositories.sales_transaction_item_repository import ISalesTransactionItemRepository
from src.domain.value_objects.sales import SalesStatus
from src.infrastructure.repositories.inventory_stock_movement_service import InventoryStockMovementService

logger = logging.getLogger(__name__)


class ConfirmSalesOrderUseCase:
    """Use case for confirming a draft sales order."""
    
    def __init__(
        self,
        sales_repository: ISalesTransactionRepository,
        sales_item_repository: ISalesTransactionItemRepository,
        stock_movement_service: InventoryStockMovementService
    ):
        """Initialize the use case with required repositories."""
        self.sales_repository = sales_repository
        self.sales_item_repository = sales_item_repository
        self.stock_movement_service = stock_movement_service
    
    async def execute(
        self,
        transaction_id: str,
        confirmed_by: Optional[str] = None
    ) -> SalesTransaction:
        """
        Confirm a draft sales order.
        
        Args:
            transaction_id: The UUID of the sales transaction
            confirmed_by: User confirming the order
            
        Returns:
            The confirmed sales transaction
            
        Raises:
            ValueError: If the transaction is not found or not in DRAFT status
        """
        # Get the transaction
        transaction = await self.sales_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Sales transaction {transaction_id} not found")
        
        # Validate status
        if transaction.status != SalesStatus.DRAFT:
            raise ValueError(
                f"Cannot confirm order with status: {transaction.status}. "
                "Only DRAFT orders can be confirmed."
            )
        
        # Get all items for final stock validation
        items = await self.sales_item_repository.get_by_transaction(transaction_id)
        
        # Validate stock availability one more time
        for item in items:
            available_stock = await self.stock_movement_service.get_available_stock(
                item.inventory_item_master_id,
                item.warehouse_id
            )
            
            if available_stock < item.quantity:
                raise ValueError(
                    f"Insufficient stock for item {item.inventory_item_master_id}. "
                    f"Available: {available_stock}, Required: {item.quantity}"
                )
        
        # Confirm the order
        transaction.confirm_order()
        
        # Update the transaction
        updated_transaction = await self.sales_repository.update(transaction)
        
        # Create stock movements to allocate inventory
        for item in items:
            await self.stock_movement_service.create_sales_movement(
                inventory_item_master_id=item.inventory_item_master_id,
                warehouse_id=item.warehouse_id,
                quantity=item.quantity,
                transaction_id=transaction.transaction_id,
                serial_numbers=item.serial_numbers,
                notes=f"Sales order {transaction.transaction_id} confirmed by {confirmed_by}"
            )
        
        logger.info(
            f"Confirmed sales order {transaction.transaction_id} with {len(items)} items"
        )
        
        return updated_transaction