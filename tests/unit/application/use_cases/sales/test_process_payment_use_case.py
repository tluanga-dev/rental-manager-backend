"""Tests for ProcessPaymentUseCase"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.application.use_cases.sales import ProcessPaymentUseCase
from src.domain.entities.sales import SalesTransaction
from src.domain.value_objects.sales import PaymentStatus


class TestProcessPaymentUseCase:
    """Test suite for ProcessPaymentUseCase"""
    
    @pytest.fixture
    def use_case(self, mock_sales_transaction_repository):
        """Create use case instance with mocked dependencies"""
        return ProcessPaymentUseCase(
            sales_transaction_repository=mock_sales_transaction_repository
        )
    
    @pytest.mark.asyncio
    async def test_process_payment_success(self, use_case, sample_sales_transaction):
        """Test successful payment processing"""
        # Setup
        sample_sales_transaction.grand_total = Decimal("1000.00")
        sample_sales_transaction.amount_paid = Decimal("0.00")
        sample_sales_transaction.payment_status = PaymentStatus.PENDING
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        # Execute
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            payment_amount=Decimal("500.00"),
            payment_method="CREDIT_CARD",
            reference_number="PAY-12345"
        )
        
        # Assert
        assert result.amount_paid == Decimal("500.00")
        assert result.payment_status == PaymentStatus.PARTIAL
        use_case.sales_transaction_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_payment_full_payment(self, use_case, sample_sales_transaction):
        """Test processing full payment"""
        sample_sales_transaction.grand_total = Decimal("750.00")
        sample_sales_transaction.amount_paid = Decimal("0.00")
        sample_sales_transaction.payment_status = PaymentStatus.PENDING
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            payment_amount=Decimal("750.00")
        )
        
        assert result.amount_paid == Decimal("750.00")
        assert result.payment_status == PaymentStatus.PAID
        assert result.balance_due == Decimal("0.00")
    
    @pytest.mark.asyncio
    async def test_process_payment_partial_to_full(self, use_case, sample_sales_transaction):
        """Test completing payment from partial status"""
        sample_sales_transaction.grand_total = Decimal("1000.00")
        sample_sales_transaction.amount_paid = Decimal("600.00")
        sample_sales_transaction.payment_status = PaymentStatus.PARTIAL
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            payment_amount=Decimal("400.00")
        )
        
        assert result.amount_paid == Decimal("1000.00")
        assert result.payment_status == PaymentStatus.PAID
    
    @pytest.mark.asyncio
    async def test_process_payment_transaction_not_found(self, use_case):
        """Test payment for non-existent transaction"""
        use_case.sales_transaction_repository.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="Sales transaction .* not found"):
            await use_case.execute(
                transaction_id=uuid4(),
                payment_amount=Decimal("100.00")
            )
    
    @pytest.mark.asyncio
    async def test_process_payment_invalid_amount(self, use_case, sample_sales_transaction):
        """Test payment with invalid amount"""
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        # Negative amount
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_amount=Decimal("-100.00")
            )
        
        # Zero amount
        with pytest.raises(ValueError, match="Payment amount must be positive"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_amount=Decimal("0.00")
            )
    
    @pytest.mark.asyncio
    async def test_process_payment_overpayment(self, use_case, sample_sales_transaction):
        """Test overpayment prevention"""
        sample_sales_transaction.grand_total = Decimal("500.00")
        sample_sales_transaction.amount_paid = Decimal("300.00")
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Payment amount .* exceeds outstanding balance"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_amount=Decimal("250.00")  # Would total 550, exceeding 500
            )
    
    @pytest.mark.asyncio
    async def test_process_payment_already_paid(self, use_case, sample_sales_transaction):
        """Test payment on already paid transaction"""
        sample_sales_transaction.grand_total = Decimal("1000.00")
        sample_sales_transaction.amount_paid = Decimal("1000.00")
        sample_sales_transaction.payment_status = PaymentStatus.PAID
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Transaction is already fully paid"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_amount=Decimal("100.00")
            )
    
    @pytest.mark.asyncio
    async def test_process_payment_cancelled_transaction(self, use_case, sample_sales_transaction):
        """Test payment on cancelled transaction"""
        from src.domain.value_objects.sales import SalesStatus
        sample_sales_transaction.status = SalesStatus.CANCELLED
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Cannot process payment for cancelled transaction"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_amount=Decimal("100.00")
            )
    
    @pytest.mark.asyncio
    async def test_process_payment_with_metadata(self, use_case, sample_sales_transaction):
        """Test payment with additional metadata"""
        sample_sales_transaction.grand_total = Decimal("500.00")
        sample_sales_transaction.amount_paid = Decimal("0.00")
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.record_payment = AsyncMock()
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            payment_amount=Decimal("200.00"),
            payment_method="BANK_TRANSFER",
            reference_number="TXN-98765",
            notes="First installment payment"
        )
        
        assert result.amount_paid == Decimal("200.00")
        
        # Verify payment was recorded with metadata
        use_case.sales_transaction_repository.record_payment.assert_called_once_with(
            transaction_id=sample_sales_transaction.id,
            amount=Decimal("200.00"),
            payment_method="BANK_TRANSFER",
            reference_number="TXN-98765",
            notes="First installment payment"
        )
    
    @pytest.mark.asyncio
    async def test_process_payment_overdue_to_paid(self, use_case, sample_sales_transaction):
        """Test payment clearing overdue status"""
        sample_sales_transaction.grand_total = Decimal("300.00")
        sample_sales_transaction.amount_paid = Decimal("0.00")
        sample_sales_transaction.payment_status = PaymentStatus.OVERDUE
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        use_case.sales_transaction_repository.update.return_value = sample_sales_transaction
        
        result = await use_case.execute(
            transaction_id=sample_sales_transaction.id,
            payment_amount=Decimal("300.00")
        )
        
        assert result.payment_status == PaymentStatus.PAID
        assert result.amount_paid == Decimal("300.00")
    
    @pytest.mark.asyncio
    async def test_process_payment_inactive_transaction(self, use_case, sample_sales_transaction):
        """Test payment on inactive transaction"""
        sample_sales_transaction.is_active = False
        
        use_case.sales_transaction_repository.get_by_id.return_value = sample_sales_transaction
        
        with pytest.raises(ValueError, match="Cannot process payment for inactive transaction"):
            await use_case.execute(
                transaction_id=sample_sales_transaction.id,
                payment_amount=Decimal("100.00")
            )