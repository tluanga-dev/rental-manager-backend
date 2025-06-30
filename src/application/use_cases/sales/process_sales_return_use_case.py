"""Process Sales Return Use Case

This module defines the use case for processing product returns.
"""

from decimal import Decimal
from typing import List, Dict, Any, Optional
from uuid import UUID
import logging

from src.domain.entities.sales import SalesReturn, SalesReturnItem
from src.domain.repositories.sales_transaction_repository import ISalesTransactionRepository
from src.domain.repositories.sales_transaction_item_repository import ISalesTransactionItemRepository
from src.domain.repositories.sales_return_repository import ISalesReturnRepository
from src.domain.repositories.sales_return_item_repository import ISalesReturnItemRepository
from src.domain.repositories.id_manager_repository import IdManagerRepository
from src.domain.value_objects.sales import PaymentStatus
from src.infrastructure.repositories.inventory_stock_movement_service import InventoryStockMovementService

logger = logging.getLogger(__name__)


class ProcessSalesReturnUseCase:
    """Use case for processing sales returns."""
    
    SALES_RETURN_PREFIX = 'SRT'
    
    def __init__(
        self,
        sales_repository: ISalesTransactionRepository,
        sales_item_repository: ISalesTransactionItemRepository,
        return_repository: ISalesReturnRepository,
        return_item_repository: ISalesReturnItemRepository,
        id_manager_repository: IdManagerRepository,
        stock_movement_service: InventoryStockMovementService
    ):
        """Initialize the use case with required repositories."""
        self.sales_repository = sales_repository
        self.sales_item_repository = sales_item_repository
        self.return_repository = return_repository
        self.return_item_repository = return_item_repository
        self.id_manager_repository = id_manager_repository
        self.stock_movement_service = stock_movement_service
    
    async def execute(
        self,
        sales_transaction_id: UUID,
        reason: str,
        items: List[Dict[str, Any]],
        restocking_fee: Decimal = Decimal("0"),
        approved_by_id: Optional[UUID] = None,
        created_by: Optional[str] = None
    ) -> SalesReturn:
        """
        Process a sales return.
        
        Args:
            sales_transaction_id: The UUID of the original sales transaction
            reason: Reason for the return
            items: List of items being returned with sales_item_id, quantity, condition, serial_numbers
            restocking_fee: Optional restocking fee
            approved_by_id: User approving the return
            created_by: User creating the return
            
        Returns:
            The created sales return
            
        Raises:
            ValueError: If validation fails
        """
        # Get the original transaction
        transaction = await self.sales_repository.get_by_id(sales_transaction_id)
        if not transaction:
            raise ValueError(f"Sales transaction {sales_transaction_id} not found")
        
        # Validate transaction can have returns
        if not transaction.can_process_return():
            raise ValueError(
                f"Cannot process return for transaction with status: {transaction.status}"
            )
        
        # Validate return items
        if not items:
            raise ValueError("At least one item must be returned")
        
        # Generate return ID
        return_id = await self.id_manager_repository.get_next_id(self.SALES_RETURN_PREFIX)
        
        # Create sales return
        sales_return = SalesReturn(
            return_id=return_id,
            sales_transaction_id=sales_transaction_id,
            reason=reason,
            restocking_fee=restocking_fee,
            approved_by_id=approved_by_id,
            created_by=created_by
        )
        
        # Save the return
        saved_return = await self.return_repository.create(sales_return)
        
        # Process return items
        total_refund = Decimal("0")
        created_return_items = []
        
        for item_data in items:
            # Get original sales item
            sales_item = await self.sales_item_repository.get_by_id(item_data['sales_item_id'])
            if not sales_item:
                raise ValueError(f"Sales item {item_data['sales_item_id']} not found")
            
            # Validate it belongs to this transaction
            if sales_item.transaction_id != sales_transaction_id:
                raise ValueError(
                    f"Sales item {sales_item.id} does not belong to "
                    f"transaction {sales_transaction_id}"
                )
            
            # Get already returned quantity
            already_returned = await self.return_item_repository.get_total_returned_quantity(
                sales_item.id
            )
            
            # Validate return quantity
            return_quantity = item_data['quantity']
            if return_quantity <= 0:
                raise ValueError("Return quantity must be greater than zero")
            
            if already_returned + return_quantity > sales_item.quantity:
                raise ValueError(
                    f"Cannot return {return_quantity} of item {sales_item.id}. "
                    f"Original quantity: {sales_item.quantity}, "
                    f"Already returned: {already_returned}"
                )
            
            # Validate serial numbers if provided
            serial_numbers = item_data.get('serial_numbers', [])
            if serial_numbers and len(serial_numbers) != return_quantity:
                raise ValueError(
                    f"Number of serial numbers ({len(serial_numbers)}) "
                    f"must match return quantity ({return_quantity})"
                )
            
            # Create return item
            return_item = SalesReturnItem(
                sales_return_id=saved_return.id,
                sales_item_id=sales_item.id,
                quantity=return_quantity,
                condition=item_data['condition'],
                serial_numbers=serial_numbers,
                created_by=created_by
            )
            
            # Save return item
            saved_return_item = await self.return_item_repository.create(return_item)
            created_return_items.append(saved_return_item)
            
            # Calculate refund for this item
            item_unit_value = sales_item.total / sales_item.quantity
            item_refund = item_unit_value * return_quantity
            total_refund += item_refund
            
            # Create stock movement to return inventory
            await self.stock_movement_service.create_return_movement(
                inventory_item_master_id=sales_item.inventory_item_master_id,
                warehouse_id=sales_item.warehouse_id,
                quantity=return_quantity,
                transaction_id=return_id,
                serial_numbers=serial_numbers,
                condition=item_data['condition'],
                notes=f"Return {return_id}: {reason}"
            )
        
        # Update return with calculated refund
        saved_return.calculate_refund(total_refund)
        updated_return = await self.return_repository.update(saved_return)
        
        # Update original transaction payment status if fully refunded
        total_returns = await self.return_repository.get_total_refund_amount(sales_transaction_id)
        if total_returns >= transaction.grand_total:
            await self.sales_repository.update_payment_status(
                sales_transaction_id,
                PaymentStatus.REFUNDED,
                transaction.amount_paid
            )
        
        logger.info(
            f"Processed return {return_id} for transaction {transaction.transaction_id} "
            f"with {len(created_return_items)} items, refund amount: {updated_return.refund_amount}"
        )
        
        return updated_return