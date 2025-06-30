"""Integration tests for SalesTransactionRepository"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.repositories.sales_transaction_repository_impl import SQLAlchemySalesTransactionRepository
from src.infrastructure.repositories.customer_repository_impl import SQLAlchemyCustomerRepository
from src.domain.entities.sales import SalesTransaction
from src.domain.entities.customer import Customer
from src.domain.value_objects.sales import SalesStatus, PaymentStatus, PaymentTerms


@pytest.mark.integration
class TestSalesTransactionRepository:
    """Integration test suite for SalesTransactionRepository"""
    
    @pytest.fixture
    async def repository(self, async_session: AsyncSession):
        """Create repository instance"""
        return SQLAlchemySalesTransactionRepository(async_session)
    
    @pytest.fixture
    async def customer_repository(self, async_session: AsyncSession):
        """Create customer repository instance"""
        return SQLAlchemyCustomerRepository(async_session)
    
    @pytest.fixture
    async def test_customer(self, customer_repository):
        """Create a test customer"""
        customer = Customer(
            name="Test Customer",
            email=f"test_{uuid4().hex[:8]}@example.com",
            address="123 Test St",
            city="Test City"
        )
        return await customer_repository.save(customer)
    
    @pytest.mark.asyncio
    async def test_create_sales_transaction(self, repository, test_customer):
        """Test creating a sales transaction"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-TEST-001",
            order_date=datetime.now(),
            status=SalesStatus.DRAFT,
            payment_status=PaymentStatus.PENDING,
            payment_terms=PaymentTerms.NET_30,
            subtotal=Decimal("100.00"),
            grand_total=Decimal("110.00")
        )
        
        saved = await repository.create(transaction)
        
        assert saved.id is not None
        assert saved.customer_id == test_customer.id
        assert saved.transaction_id == "SO-TEST-001"
        assert saved.status == SalesStatus.DRAFT
        assert saved.payment_status == PaymentStatus.PENDING
        assert saved.grand_total == Decimal("110.00")
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, repository, test_customer):
        """Test retrieving transaction by ID"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-TEST-002",
            order_date=datetime.now()
        )
        saved = await repository.create(transaction)
        
        found = await repository.get_by_id(saved.id)
        
        assert found is not None
        assert found.id == saved.id
        assert found.transaction_id == "SO-TEST-002"
    
    @pytest.mark.asyncio
    async def test_get_by_transaction_id(self, repository, test_customer):
        """Test retrieving transaction by transaction ID"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-TEST-003",
            order_date=datetime.now()
        )
        await repository.create(transaction)
        
        found = await repository.get_by_transaction_id("SO-TEST-003")
        
        assert found is not None
        assert found.transaction_id == "SO-TEST-003"
    
    @pytest.mark.asyncio
    async def test_get_by_invoice_number(self, repository, test_customer):
        """Test retrieving transaction by invoice number"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-TEST-004",
            invoice_number="INV-TEST-001",
            order_date=datetime.now()
        )
        await repository.create(transaction)
        
        found = await repository.get_by_invoice_number("INV-TEST-001")
        
        assert found is not None
        assert found.invoice_number == "INV-TEST-001"
    
    @pytest.mark.asyncio
    async def test_get_by_customer(self, repository, test_customer, customer_repository):
        """Test retrieving transactions by customer"""
        # Create another customer
        other_customer = Customer(
            name="Other Customer",
            email=f"other_{uuid4().hex[:8]}@example.com",
            address="456 Other St",
            city="Other City"
        )
        other_customer = await customer_repository.save(other_customer)
        
        # Create transactions for both customers
        for i in range(3):
            await repository.create(SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=f"SO-CUST1-{i}",
                order_date=datetime.now()
            ))
        
        await repository.create(SalesTransaction(
            customer_id=other_customer.id,
            transaction_id="SO-CUST2-1",
            order_date=datetime.now()
        ))
        
        # Get transactions for test customer
        transactions = await repository.get_by_customer(test_customer.id)
        
        assert len(transactions) == 3
        assert all(t.customer_id == test_customer.id for t in transactions)
    
    @pytest.mark.asyncio
    async def test_get_by_status(self, repository, test_customer):
        """Test retrieving transactions by status"""
        # Create transactions with different statuses
        statuses = [SalesStatus.DRAFT, SalesStatus.CONFIRMED, SalesStatus.CONFIRMED, 
                   SalesStatus.PROCESSING, SalesStatus.DELIVERED]
        
        for i, status in enumerate(statuses):
            await repository.create(SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=f"SO-STATUS-{i}",
                order_date=datetime.now(),
                status=status
            ))
        
        # Get confirmed transactions
        confirmed = await repository.get_by_status(SalesStatus.CONFIRMED)
        
        assert len(confirmed) == 2
        assert all(t.status == SalesStatus.CONFIRMED for t in confirmed)
    
    @pytest.mark.asyncio
    async def test_get_by_payment_status(self, repository, test_customer):
        """Test retrieving transactions by payment status"""
        # Create transactions with different payment statuses
        payment_statuses = [PaymentStatus.PENDING, PaymentStatus.PENDING, 
                           PaymentStatus.PARTIAL, PaymentStatus.PAID]
        
        for i, payment_status in enumerate(payment_statuses):
            await repository.create(SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=f"SO-PAY-{i}",
                order_date=datetime.now(),
                payment_status=payment_status
            ))
        
        # Get pending payments
        pending = await repository.get_by_payment_status(PaymentStatus.PENDING)
        
        assert len(pending) == 2
        assert all(t.payment_status == PaymentStatus.PENDING for t in pending)
    
    @pytest.mark.asyncio
    async def test_get_overdue_transactions(self, repository, test_customer):
        """Test retrieving overdue transactions"""
        # Create transactions with different due dates
        today = date.today()
        
        # Overdue transaction
        overdue = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-OVERDUE-1",
            order_date=datetime.now() - timedelta(days=40),
            payment_status=PaymentStatus.PENDING,
            payment_due_date=today - timedelta(days=10),
            grand_total=Decimal("500.00")
        )
        await repository.create(overdue)
        
        # Not yet due
        future = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-FUTURE-1",
            order_date=datetime.now(),
            payment_status=PaymentStatus.PENDING,
            payment_due_date=today + timedelta(days=10),
            grand_total=Decimal("300.00")
        )
        await repository.create(future)
        
        # Paid transaction (not overdue even if past due date)
        paid = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-PAID-1",
            order_date=datetime.now() - timedelta(days=40),
            payment_status=PaymentStatus.PAID,
            payment_due_date=today - timedelta(days=5),
            grand_total=Decimal("200.00")
        )
        await repository.create(paid)
        
        # Get overdue transactions
        overdue_list = await repository.get_overdue_transactions()
        
        assert len(overdue_list) == 1
        assert overdue_list[0].transaction_id == "SO-OVERDUE-1"
    
    @pytest.mark.asyncio
    async def test_update_transaction(self, repository, test_customer):
        """Test updating a transaction"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-UPDATE-1",
            order_date=datetime.now(),
            status=SalesStatus.DRAFT,
            notes="Original notes"
        )
        saved = await repository.create(transaction)
        
        # Update transaction
        saved.status = SalesStatus.CONFIRMED
        saved.notes = "Updated notes"
        saved.shipping_address = "789 New Address"
        
        updated = await repository.update(saved)
        
        assert updated.status == SalesStatus.CONFIRMED
        assert updated.notes == "Updated notes"
        assert updated.shipping_address == "789 New Address"
    
    @pytest.mark.asyncio
    async def test_delete_transaction(self, repository, test_customer):
        """Test soft deleting a transaction"""
        transaction = SalesTransaction(
            customer_id=test_customer.id,
            transaction_id="SO-DELETE-1",
            order_date=datetime.now()
        )
        saved = await repository.create(transaction)
        
        # Delete transaction
        await repository.delete(saved.id)
        
        # Try to find it
        found = await repository.get_by_id(saved.id)
        assert found.is_active is False
    
    @pytest.mark.asyncio
    async def test_search_transactions(self, repository, test_customer):
        """Test searching transactions"""
        # Create transactions with searchable content
        transactions_data = [
            ("SO-SEARCH-1", "INV-SEARCH-1", "Notes about laptop order"),
            ("SO-SEARCH-2", "INV-SEARCH-2", "Rush delivery for printer"),
            ("SO-SEARCH-3", "INV-SEARCH-3", "Customer requested blue color")
        ]
        
        for tid, inv, notes in transactions_data:
            await repository.create(SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=tid,
                invoice_number=inv,
                order_date=datetime.now(),
                notes=notes
            ))
        
        # Search for "laptop"
        results = await repository.search("laptop")
        assert len(results) == 1
        assert "laptop" in results[0].notes.lower()
        
        # Search for "SEARCH"
        results = await repository.search("SEARCH")
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_get_next_transaction_id(self, repository):
        """Test getting next transaction ID"""
        # This would typically use the ID manager service
        # For now, we'll test the pattern
        next_id = await repository.get_next_transaction_id()
        
        assert next_id is not None
        assert isinstance(next_id, str)
        assert next_id.startswith("SO-")
    
    @pytest.mark.asyncio
    async def test_list_with_filters(self, repository, test_customer, customer_repository):
        """Test listing transactions with various filters"""
        # Create another customer
        other_customer = Customer(
            name="Filter Customer",
            email=f"filter_{uuid4().hex[:8]}@example.com",
            address="789 Filter St",
            city="Filter City"
        )
        other_customer = await customer_repository.save(other_customer)
        
        # Create test data
        base_date = datetime.now()
        for i in range(5):
            await repository.create(SalesTransaction(
                customer_id=test_customer.id if i < 3 else other_customer.id,
                transaction_id=f"SO-LIST-{i}",
                order_date=base_date - timedelta(days=i),
                status=SalesStatus.CONFIRMED if i % 2 == 0 else SalesStatus.DRAFT,
                payment_status=PaymentStatus.PAID if i < 2 else PaymentStatus.PENDING,
                grand_total=Decimal(str(100 * (i + 1)))
            ))
        
        # Test customer filter
        filters = {"customer_id": test_customer.id}
        results = await repository.list(filters=filters)
        assert len(results) == 3
        
        # Test status filter
        filters = {"status": SalesStatus.CONFIRMED}
        results = await repository.list(filters=filters)
        assert all(t.status == SalesStatus.CONFIRMED for t in results)
        
        # Test date range filter
        filters = {
            "start_date": base_date - timedelta(days=3),
            "end_date": base_date - timedelta(days=1)
        }
        results = await repository.list(filters=filters)
        assert len(results) == 3
        
        # Test pagination
        results = await repository.list(skip=2, limit=2)
        assert len(results) == 2
    
    @pytest.mark.asyncio
    async def test_get_sales_summary(self, repository, test_customer):
        """Test getting sales summary statistics"""
        # Create test transactions
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        transactions_data = [
            (Decimal("100.00"), PaymentStatus.PAID),
            (Decimal("200.00"), PaymentStatus.PAID),
            (Decimal("150.00"), PaymentStatus.PARTIAL),
            (Decimal("300.00"), PaymentStatus.PENDING),
        ]
        
        for amount, payment_status in transactions_data:
            await repository.create(SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=f"SO-SUM-{amount}",
                order_date=datetime.now() - timedelta(days=3),
                grand_total=amount,
                payment_status=payment_status,
                status=SalesStatus.CONFIRMED
            ))
        
        # Get summary
        summary = await repository.get_sales_summary(start_date, end_date)
        
        assert summary["total_sales"] == Decimal("750.00")  # Sum of all
        assert summary["total_orders"] == 4
        assert summary["paid_amount"] == Decimal("300.00")  # Sum of paid only
        # pending_amount would include PARTIAL and PENDING
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self, repository, test_customer):
        """Test repository handles concurrent access properly"""
        import asyncio
        
        async def create_transaction(index):
            transaction = SalesTransaction(
                customer_id=test_customer.id,
                transaction_id=f"SO-CONCURRENT-{index}",
                order_date=datetime.now(),
                grand_total=Decimal(str(100 * index))
            )
            return await repository.create(transaction)
        
        # Create multiple transactions concurrently
        tasks = [create_transaction(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(r.id is not None for r in results)
        assert len(set(r.id for r in results)) == 5  # All unique IDs