"""Update Payment Use Case

This module defines the use case for updating payment information on a sales transaction.
"""

from decimal import Decimal
from typing import Optional

import logging

from src.domain.entities.sales import SalesTransaction
from src.domain.repositories.sales_transaction_repository import ISalesTransactionRepository
from src.domain.value_objects.sales import PaymentStatus

logger = logging.getLogger(__name__)


class UpdatePaymentUseCase:
    """Use case for updating payment information."""
    
    def __init__(self, sales_repository: ISalesTransactionRepository):
        """Initialize the use case with required repository."""
        self.sales_repository = sales_repository
    
    async def execute(
        self,
        transaction_id: str,
        amount_paid: Decimal,
        payment_notes: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> SalesTransaction:
        """
        Update payment information for a sales transaction.
        
        Args:
            transaction_id: The UUID of the sales transaction
            amount_paid: The total amount paid (not incremental)
            payment_notes: Optional notes about the payment
            updated_by: User updating the payment
            
        Returns:
            The updated sales transaction
            
        Raises:
            ValueError: If the transaction is not found or payment is invalid
        """
        # Get the transaction
        transaction = await self.sales_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError(f"Sales transaction {transaction_id} not found")
        
        # Validate amount
        if amount_paid < Decimal("0"):
            raise ValueError("Payment amount cannot be negative")
        
        if amount_paid > transaction.grand_total:
            raise ValueError(
                f"Payment amount ({amount_paid}) cannot exceed "
                f"grand total ({transaction.grand_total})"
            )
        
        # Update payment
        previous_amount = transaction.amount_paid
        transaction.update_payment(amount_paid, payment_notes)
        
        # Add audit note
        if updated_by:
            audit_note = f"Payment updated by {updated_by}: {previous_amount} -> {amount_paid}"
            if transaction.notes:
                transaction.notes = f"{transaction.notes}\n{audit_note}"
            else:
                transaction.notes = audit_note
        
        # Update the transaction
        updated_transaction = await self.sales_repository.update(transaction)
        
        logger.info(
            f"Updated payment for transaction {transaction.transaction_id}: "
            f"amount_paid={amount_paid}, status={transaction.payment_status}"
        )
        
        return updated_transaction