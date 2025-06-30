"""Tests for UpdateSalesTransactionUseCase"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.application.use_cases.sales import UpdateSalesTransactionUseCase
from src.domain.entities.sales import SalesTransaction
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms


class TestUpdateSalesTransactionUseCase:
    """Test suite for UpdateSalesTransactionUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_sales_transaction_repository):
        """Create use case instance with mocked dependencies"""
        return UpdateSalesTransactionUseCase(
            sales_transaction_repository=mock_sales_transaction_repository
        )
    
    @pytest.mark.asyncio
    async def test_update_transaction_success(self, use_case, sample_sales_transaction):
        """Test successful transaction update"""
        # Setup
        sample_sales_transaction.status = SalesStatus.DRAFT
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        # Execute
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            status="CONFIRMED",
            shipping_address="New shipping address",
            notes="Updated notes"
        )
        
        # Assert
        assert result.status == SalesStatus.CONFIRMED
        assert result.shipping_address == "New shipping address"
        assert result.notes == "Updated notes"
        use_case.sales_transaction_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_transaction_not_found(self, use_case):
        """Test updating non-existent transaction"""
        use_case.sales_transaction_repository.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Sales transaction .* not found"):
            await use_case.execute(
                transaction_id=uuid4(),
                notes="New notes"
            )
    
    @pytest.mark.asyncio
    async def test_update_transaction_invalid_status_transition(self, use_case, sample_sales_transaction):
        """Test invalid status transition"""
        sample_sales_transaction.status = SalesStatus.DELIVERED
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Cannot transition from .* to .*"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                status="DRAFT"
            )
    
    @pytest.mark.asyncio
    async def test_update_transaction_payment_status(self, use_case, sample_sales_transaction):
        """Test updating payment status"""
        sample_sales_transaction.payment_status = PaymentStatus.PENDING
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            payment_status="PARTIAL"
        )
        
        assert result.payment_status == PaymentStatus.PARTIAL
    
    @pytest.mark.asyncio
    async def test_update_transaction_invalid_payment_status_transition(self, use_case, sample_sales_transaction):
        """Test invalid payment status transition"""
        sample_sales_transaction.payment_status = PaymentStatus.REFUNDED
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Cannot transition from .* to .*"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_status="PENDING"
            )
    
    @pytest.mark.asyncio
    async def test_update_transaction_delivery_date(self, use_case, sample_sales_transaction):
        """Test updating delivery date"""
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        new_date = datetime(2024, 12, 25, 10, 0, 0)
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            delivery_date=new_date
        )
        
        assert result.delivery_date == new_date
    
    @pytest.mark.asyncio
    async def test_update_transaction_addresses(self, use_case, sample_sales_transaction):
        """Test updating shipping and billing addresses"""
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            shipping_address="123 New Shipping St",
            billing_address="456 New Billing Ave"
        )
        
        assert result.shipping_address == "123 New Shipping St"
        assert result.billing_address == "456 New Billing Ave"
    
    @pytest.mark.asyncio
    async def test_update_transaction_customer_notes(self, use_case, sample_sales_transaction):
        """Test updating customer notes"""
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            customer_notes="Please deliver to back entrance"
        )
        
        assert result.customer_notes == "Please deliver to back entrance"
    
    @pytest.mark.asyncio
    async def test_update_transaction_multiple_fields(self, use_case, sample_sales_transaction):
        """Test updating multiple fields at once"""
        sample_sales_transaction.status = SalesStatus.CONFIRMED
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            status="PROCESSING",
            shipping_address="789 Express Lane",
            notes="Priority shipping",
            customer_notes="Leave at doorstep"
        )
        
        assert result.status == SalesStatus.PROCESSING
        assert result.shipping_address == "789 Express Lane"
        assert result.notes == "Priority shipping"
        assert result.customer_notes == "Leave at doorstep"
    
    @pytest.mark.asyncio
    async def test_update_cancelled_transaction(self, use_case, sample_sales_transaction):
        """Test that cancelled transactions cannot be updated"""
        sample_sales_transaction.status = SalesStatus.CANCELLED
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Cannot update cancelled transaction"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                notes="Try to update"
            )
    
    @pytest.mark.asyncio
    async def test_update_inactive_transaction(self, use_case, sample_sales_transaction):
        """Test that inactive transactions cannot be updated"""
        sample_sales_transaction.is_active = False
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Cannot update inactive transaction"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                notes="Try to update"
            )
    
    @pytest.mark.asyncio
    async def test_update_with_invalid_enum_value(self, use_case, sample_sales_transaction):
        """Test update with invalid enum value"""
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Invalid status"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                status="INVALID_STATUS"
            )
    
    @pytest.mark.asyncio
    async def test_update_no_changes(self, use_case, sample_sales_transaction):
        """Test update with no actual changes"""
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        # Execute with no changes
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id
        )
        
        # Should still call update (for updated_at timestamp)
        assert result == sample_sales_transaction
        use_case.sales_transaction_repository.update.assert_called_once()