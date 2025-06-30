"""Integration tests for SalesReturnRepository"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.sales_return_repository_impl import SQLAlchemySalesReturnRepository
from src.infrastructure.repositories.sales_transaction_repository_impl import SQLAlchemySalesTransactionRepository
from src.infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from src.domain.entities.sales import SalesReturn, SalesTransaction
from src.domain.entities.customer import Customer
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms


@pytest.mark.integration
class TestSalesReturnRepository:
    """Integration test suite for SalesReturnRepository"""
    
    @pytest.fixture
    async def repository(self, async_session: AsyncSession):
        """Create repository instance"""
        return SQLAlchemySalesReturnRepository(async_session)
    
    @pytest.fixture
    async def sales_repository(self, async_session: AsyncSession):
        """Create sales transaction repository instance"""
        return SQLAlchemySalesTransactionRepository(async_session)
    
    @pytest.fixture
    async def customer_repository(self, async_session: AsyncSession):
        """Create customer repository instance"""
        return SQLAlchemyCustomerRepository(async_session)
    
    @pytest.fixture
    async def test_customer(self, customer_repository):
        """Create a test customer"""
        customer = Customer(
            name="Return Test Customer",
            email=f"return_{uuid4().hex[:8]}@example.com",
            address="123 Return St",
            city="Return City"
        )
        return await customer_repository.save(customer)
    
    @pytest.fixture
    async def test_transaction(self, sales_repository, test_customer):
        """Create a test sales transaction"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id=f"SO-RET-{uuid4().hex[:8]}",
            order_date=datetime.now(),
            status=SalesStatus.DELIVERED,
            payment_status=PaymentStatus.PAID,
            grand_total=Decimal("500.00")
        )
        return await sales_repository.create(transaction)
    
    @pytest.mark.asyncio
    async def test_create_sales_return(self, repository, test_transaction):
        """Test creating a sales return"""
        sales_return = SalesReturn(
            return_id="RET-TEST-001",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Customer changed mind",
            refund_amount=Decimal("400.00"),
            restocking_fee=Decimal("40.00")
        )
        
        saved = await repository.create(sales_return)
        
        assert saved.id is not None
        assert saved.sales_transaction_id == test_transaction.id
        assert saved.return_id == "RET-TEST-001"
        assert saved.reason == "Customer changed mind"
        assert saved.refund_amount == Decimal("400.00")
        assert saved.restocking_fee == Decimal("40.00")
        assert saved.net_refund_amount == Decimal("360.00")
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, repository, test_transaction):
        """Test retrieving return by ID"""
        sales_return = SalesReturn(
            return_id="RET-TEST-002",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Product defective",
            refund_amount=Decimal("500.00")
        )
        saved = await repository.create(sales_return)
        
        found = await repository.get_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
        assert found.return_id == "RET-TEST-002"
        assert found.reason == "Product defective"
    
    @pytest.mark.asyncio
    async def test_get_by_return_id(self, repository, test_transaction):
        """Test retrieving return by return ID"""
        sales_return = SalesReturn(
            return_id="RET-TEST-003",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Wrong item shipped"
        )
        await repository.create(sales_return)
        
        found = await repository.get_by_return_id("RET-TEST-003")
        
        assert found is not None
        assert found.return_id == "RET-TEST-003"
    
    @pytest.mark.asyncio
    async def test_get_by_transaction(self, repository, sales_repository, test_customer):
        """Test retrieving returns by transaction"""
        # Create two transactions
        transaction1 = await sales_repository.create(SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-MULTI-1",
            order_date=datetime.now(),
            status=SalesStatus.DELIVERED
        ))
        
        transaction2 = await sales_repository.create(SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-MULTI-2",
            order_date=datetime.now(),
            status=SalesStatus.DELIVERED
        ))
        
        # Create returns for first transaction
        for i in range(2):
            await repository.create(SalesReturn(
                return_id=f"RET-MULTI-1-{i}",
                sales_transaction_id=transaction1.id,
                return_date=datetime.now(),
                reason=f"Reason {i}",
                refund_amount=Decimal("100.00")
            ))
        
        # Create return for second transaction
        await repository.create(SalesReturn(
            return_id="RET-MULTI-2-1",
            sales_transaction_id=transaction2.id,
            return_date=datetime.now(),
            reason="Different reason",
            refund_amount=Decimal("200.00")
        ))
        
        # Get returns for first transaction
        returns = await repository.get_by_transaction(transaction1.id)
        
        assert len(returns) == 2
        assert all(r.sales_transaction_id == transaction1.id for r in returns)
    
    @pytest.mark.asyncio
    async def test_get_pending_approval(self, repository, test_transaction):
        """Test retrieving returns pending approval"""
        # Create approved return
        approved = SalesReturn(
            return_id="RET-APPROVED-1",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Approved return",
            refund_amount=Decimal("100.00"),
            approved_by_id=uuid4()
        )
        await repository.create(approved)
        
        # Create pending returns
        for i in range(3):
            await repository.create(SalesReturn(
                return_id=f"RET-PENDING-{i}",
                sales_transaction_id=test_transaction.id,
                return_date=datetime.now(),
                reason=f"Pending reason {i}",
                refund_amount=Decimal("50.00")
            ))
        
        # Get pending returns
        pending = await repository.get_pending_approval()
        
        assert len(pending) == 3
        assert all(r.approved_by_id is None for r in pending)
        assert all(not r.is_approved for r in pending)
    
    @pytest.mark.asyncio
    async def test_approve_return(self, repository, test_transaction):
        """Test approving a return"""
        sales_return = SalesReturn(
            return_id="RET-APPROVE-1",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="To be approved",
            refund_amount=Decimal("300.00")
        )
        saved = await repository.create(sales_return)
        
        # Approve the return
        approver_id = uuid4()
        approved = await repository.approve(saved.id, approver_id)
        
        assert approved.approved_by_id == approver_id
        assert approved.is_approved is True
        
        # Verify it's no longer in pending
        pending = await repository.get_pending_approval()
        assert saved.id not in [r.id for r in pending]
    
    @pytest.mark.asyncio
    async def test_approve_already_approved(self, repository, test_transaction):
        """Test approving an already approved return"""
        approver_id = uuid4()
        sales_return = SalesReturn(
            return_id="RET-DOUBLE-1",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Already approved",
            refund_amount=Decimal("200.00"),
            approved_by_id=approver_id
        )
        saved = await repository.create(sales_return)
        
        # Try to approve again
        with pytest.raises(ValueError, match="already approved"):
            await repository.approve(saved.id, uuid4())
    
    @pytest.mark.asyncio
    async def test_update_return(self, repository, test_transaction):
        """Test updating a return"""
        sales_return = SalesReturn(
            return_id="RET-UPDATE-1",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Original reason",
            refund_amount=Decimal("150.00"),
            restocking_fee=Decimal("15.00")
        )
        saved = await repository.create(sales_return)
        
        # Update return
        saved.reason = "Updated reason with more details"
        saved.restocking_fee = Decimal("20.00")
        
        updated = await repository.update(saved)
        
        assert updated.reason == "Updated reason with more details"
        assert updated.restocking_fee == Decimal("20.00")
        assert updated.net_refund_amount == Decimal("130.00")
    
    @pytest.mark.asyncio
    async def test_delete_return(self, repository, test_transaction):
        """Test soft deleting a return"""
        sales_return = SalesReturn(
            return_id="RET-DELETE-1",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="To be deleted",
            refund_amount=Decimal("100.00")
        )
        saved = await repository.create(sales_return)
        
        # Delete return
        await repository.delete(saved.id)
        
        # Verify it's soft deleted
        found = await repository.get_by_id(saved.id)
        assert found.is_active is False
    
    @pytest.mark.asyncio
    async def test_list_with_filters(self, repository, sales_repository, test_customer):
        """Test listing returns with filters"""
        # Create transactions with different dates
        base_date = datetime.now()
        transactions = []
        
        for i in range(3):
            transaction = await sales_repository.create(SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=f"SO-FILTER-{i}",
                order_date=base_date - timedelta(days=i*10),
                status=SalesStatus.DELIVERED
            ))
            transactions.append(transaction)
        
        # Create returns with different dates and approvers
        approver1 = uuid4()
        approver2 = uuid4()
        
        # Return 1: Recent, approved by approver1
        await repository.create(SalesReturn(
            return_id="RET-FILTER-1",
            sales_transaction_id=transactions[0].id,
            return_date=base_date - timedelta(days=1),
            reason="Recent approved",
            refund_amount=Decimal("100.00"),
            approved_by_id=approver1
        ))
        
        # Return 2: Old, approved by approver2
        await repository.create(SalesReturn(
            return_id="RET-FILTER-2",
            sales_transaction_id=transactions[1].id,
            return_date=base_date - timedelta(days=10),
            reason="Old approved",
            refund_amount=Decimal("200.00"),
            approved_by_id=approver2
        ))
        
        # Return 3: Recent, not approved
        await repository.create(SalesReturn(
            return_id="RET-FILTER-3",
            sales_transaction_id=transactions[2].id,
            return_date=base_date - timedelta(days=2),
            reason="Recent pending",
            refund_amount=Decimal("150.00")
        ))
        
        # Test date range filter
        filters = {
            "start_date": base_date - timedelta(days=5),
            "end_date": base_date
        }
        results = await repository.list(filters=filters)
        assert len(results) == 2  # Returns 1 and 3
        
        # Test approver filter
        filters = {"approved_by_id": approver1}
        results = await repository.list(filters=filters)
        assert len(results) == 1
        assert results[0].return_id == "RET-FILTER-1"
        
        # Test transaction filter
        filters = {"sales_transaction_id": transactions[1].id}
        results = await repository.list(filters=filters)
        assert len(results) == 1
        assert results[0].return_id == "RET-FILTER-2"
    
    @pytest.mark.asyncio
    async def test_get_return_summary(self, repository, test_transaction):
        """Test getting return summary statistics"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # Create test returns
        returns_data = [
            (Decimal("100.00"), Decimal("10.00"), True),   # Approved
            (Decimal("200.00"), Decimal("20.00"), True),   # Approved
            (Decimal("150.00"), Decimal("0.00"), False),   # Pending
            (Decimal("300.00"), Decimal("30.00"), False),  # Pending
        ]
        
        for i, (refund, fee, approved) in enumerate(returns_data):
            sales_return = SalesReturn(
                return_id=f"RET-SUM-{i}",
                sales_transaction_id=test_transaction.id,
                return_date=datetime.now() - timedelta(days=3),
                reason=f"Summary test {i}",
                refund_amount=refund,
                restocking_fee=fee,
                approved_by_id=uuid4() if approved else None
            )
            await repository.create(sales_return)
        
        # Get summary
        summary = await repository.get_return_summary(start_date, end_date)
        
        assert summary["total_returns"] == 4
        assert summary["total_refund_amount"] == Decimal("750.00")
        assert summary["total_restocking_fees"] == Decimal("60.00")
        assert summary["approved_count"] == 2
        assert summary["pending_count"] == 2
        assert summary["approved_refund_amount"] == Decimal("300.00")
        assert summary["pending_refund_amount"] == Decimal("450.00")
    
    @pytest.mark.asyncio
    async def test_get_next_return_id(self, repository):
        """Test getting next return ID"""
        next_id = await repository.get_next_return_id()
        
        assert next_id is not None
        assert isinstance(next_id, str)
        assert next_id.startswith("RET-") or next_id.startswith("SR-")
    
    @pytest.mark.asyncio
    async def test_return_with_no_restocking_fee(self, repository, test_transaction):
        """Test return with zero restocking fee"""
        sales_return = SalesReturn(
            return_id="RET-NOFEE-1",
            sales_transaction_id=test_transaction.id,
            return_date=datetime.now(),
            reason="Defective product - no restocking fee",
            refund_amount=Decimal("250.00"),
            restocking_fee=Decimal("0.00")
        )
        
        saved = await repository.create(sales_return)
        
        assert saved.restocking_fee == Decimal("0.00")
        assert saved.net_refund_amount == saved.refund_amount