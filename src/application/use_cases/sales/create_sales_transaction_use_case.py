"""Create Sales Transaction Use Case

This module defines the use case for creating a new sales transaction.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
import logging

from src.domain.entities.sales import SalesTransaction, SalesTransactionItem
from src.domain.repositories.sales_transaction_repository import ISalesTransactionRepository
from src.domain.repositories.sales_transaction_item_repository import ISalesTransactionItemRepository
from src.domain.repositories.inventory_item_master_repository import InventoryItemMasterRepository
from src.domain.repositories.id_manager_repository import IdManagerRepository
from src.domain.repositories.customer_repository import CustomerRepository
from src.domain.repositories.warehouse_repository import WarehouseRepository
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms
from src.infrastructure.repositories.inventory_stock_movement_service import InventoryStockMovementService

logger = logging.getLogger(__name__)


class CreateSalesTransactionUseCase:
    """Use case for creating a new sales transaction."""
    
    SALES_TRANSACTION_PREFIX = 'SLS'
    
    def __init__(
        self,
        sales_repository: ISalesTransactionRepository,
        sales_item_repository: ISalesTransactionItemRepository,
        customer_repository: CustomerRepository,
        inventory_repository: InventoryItemMasterRepository,
        warehouse_repository: WarehouseRepository,
        id_manager_repository: IdManagerRepository,
        stock_movement_service: InventoryStockMovementService
    ):
        """Initialize the use case with required repositories."""
        self.sales_repository = sales_repository
        self.sales_item_repository = sales_item_repository
        self.customer_repository = customer_repository
        self.inventory_repository = inventory_repository
        self.warehouse_repository = warehouse_repository
        self.id_manager_repository = id_manager_repository
        self.stock_movement_service = stock_movement_service
    
    async def execute(
        self,
        customer_id: UUID,
        items: List[Dict[str, Any]],
        order_date: Optional[datetime] = None,
        delivery_date: Optional[datetime] = None,
        payment_terms: PaymentTerms = PaymentTerms.IMMEDIATE,
        shipping_amount: Decimal = Decimal("0"),
        shipping_address: Optional[str] = None,
        billing_address: Optional[str] = None,
        purchase_order_number: Optional[str] = None,
        sales_person_id: Optional[UUID] = None,
        notes: Optional[str] = None,
        customer_notes: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Tuple[SalesTransaction, List[SalesTransactionItem]]:
        """
        Create a new sales transaction with items.
        
        Args:
            customer_id: The customer's UUID
            items: List of item dictionaries with inventory_item_master_id, warehouse_id, quantity, etc.
            order_date: Order date (defaults to now)
            delivery_date: Expected delivery date
            payment_terms: Payment terms
            shipping_amount: Shipping charges
            shipping_address: Shipping address
            billing_address: Billing address
            purchase_order_number: Customer's PO number
            sales_person_id: Sales person's UUID
            notes: Internal notes
            customer_notes: Customer notes
            created_by: User creating the transaction
            
        Returns:
            Tuple of (created SalesTransaction, list of created SalesTransactionItems)
            
        Raises:
            ValueError: If validation fails
        """
        # Validate customer exists
        customer = await self.customer_repository.find_by_id(customer_id)
        if not customer:
            raise ValueError(f"Customer with id {customer_id} not found")
        
        # Validate items
        if not items:
            raise ValueError("At least one item is required")
        
        # Check stock availability for all items
        await self._validate_stock_availability(items)
        
        # Check credit limit if applicable
        if payment_terms != PaymentTerms.PREPAID:
            await self._check_credit_limit(customer_id, items, shipping_amount)
        
        # Generate transaction ID
        transaction_id = await self.id_manager_repository.get_next_id(self.SALES_TRANSACTION_PREFIX)
        
        # Generate invoice number
        invoice_number = self._generate_invoice_number()
        
        # Create sales transaction
        sales_transaction = SalesTransaction(
            transaction_id=transaction_id,
            invoice_number=invoice_number,
            customer_id=customer_id,
            order_date=order_date or datetime.now(),
            delivery_date=delivery_date,
            status=SalesStatus.DRAFT,
            payment_status=PaymentStatus.PENDING,
            payment_terms=payment_terms,
            shipping_amount=shipping_amount,
            shipping_address=shipping_address or customer.address,
            billing_address=billing_address or customer.address,
            purchase_order_number=purchase_order_number,
            sales_person_id=sales_person_id,
            notes=notes,
            customer_notes=customer_notes,
            created_by=created_by
        )
        
        # Save the transaction first
        saved_transaction = await self.sales_repository.create(sales_transaction)
        
        # Process items
        created_items = []
        subtotal = Decimal("0")
        total_tax = Decimal("0")
        total_discount = Decimal("0")
        
        for item_data in items:
            # Validate item
            inventory_item = await self.inventory_repository.find_by_id(item_data['inventory_item_master_id'])
            if not inventory_item:
                raise ValueError(f"Inventory item {item_data['inventory_item_master_id']} not found")
            
            warehouse = await self.warehouse_repository.find_by_id(item_data['warehouse_id'])
            if not warehouse:
                raise ValueError(f"Warehouse {item_data['warehouse_id']} not found")
            
            # Create sales transaction item
            quantity = item_data['quantity']
            unit_price = item_data.get('unit_price', Decimal("0"))  # Should get from pricing service
            discount_percentage = Decimal(str(item_data.get('discount_percentage', 0)))
            tax_rate = Decimal(str(item_data.get('tax_rate', 0)))
            
            # Apply automatic bulk discount if no discount specified
            if discount_percentage == Decimal("0"):
                if quantity >= 50:
                    discount_percentage = Decimal("10")
                elif quantity >= 10:
                    discount_percentage = Decimal("5")
            
            # Get cost price (simplified - should get from inventory)
            cost_price = Decimal("0")  # Should calculate average cost
            
            sales_item = SalesTransactionItem(
                transaction_id=saved_transaction.id,
                inventory_item_master_id=inventory_item.id,
                warehouse_id=warehouse.id,
                quantity=quantity,
                unit_price=unit_price,
                cost_price=cost_price,
                discount_percentage=discount_percentage,
                tax_rate=tax_rate,
                serial_numbers=item_data.get('serial_numbers', []),
                notes=item_data.get('notes'),
                created_by=created_by
            )
            
            # Calculate totals
            sales_item.calculate_totals()
            
            # Save the item
            saved_item = await self.sales_item_repository.create(sales_item)
            created_items.append(saved_item)
            
            # Update transaction totals
            subtotal += saved_item.subtotal + saved_item.discount_amount
            total_tax += saved_item.tax_amount
            total_discount += saved_item.discount_amount
        
        # Update transaction totals
        saved_transaction.calculate_totals(subtotal, total_tax, total_discount)
        updated_transaction = await self.sales_repository.update(saved_transaction)
        
        logger.info(
            f"Created sales transaction {transaction_id} for customer {customer_id} "
            f"with {len(created_items)} items"
        )
        
        return updated_transaction, created_items
    
    async def _validate_stock_availability(self, items: List[Dict[str, Any]]) -> None:
        """Validate that all requested items have sufficient stock."""
        for item_data in items:
            inventory_item_id = item_data['inventory_item_master_id']
            warehouse_id = item_data['warehouse_id']
            requested_quantity = item_data['quantity']
            
            # Check available stock
            available_stock = await self.stock_movement_service.get_available_stock(
                inventory_item_id, warehouse_id
            )
            
            if available_stock < requested_quantity:
                inventory_item = await self.inventory_repository.find_by_id(inventory_item_id)
                warehouse = await self.warehouse_repository.find_by_id(warehouse_id)
                raise ValueError(
                    f"Insufficient stock for {inventory_item.name} at {warehouse.name}. "
                    f"Available: {available_stock}, Requested: {requested_quantity}"
                )
    
    async def _check_credit_limit(
        self,
        customer_id: UUID,
        items: List[Dict[str, Any]],
        shipping_amount: Decimal
    ) -> None:
        """Check if the customer has sufficient credit limit."""
        # Get customer's outstanding balance
        outstanding_balance = await self.sales_repository.get_customer_outstanding_balance(customer_id)
        
        # Calculate order total (simplified)
        order_total = shipping_amount
        for item in items:
            unit_price = Decimal(str(item.get('unit_price', 0)))
            quantity = item['quantity']
            order_total += unit_price * quantity
        
        # Check against credit limit (simplified - should get from customer service)
        # For now, we'll skip this check
        pass
    
    def _generate_invoice_number(self) -> str:
        """Generate a unique invoice number."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"INV-{timestamp}"