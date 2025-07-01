"""
Unit tests for Purchase Transaction API Layer.

Tests API endpoints and schemas with mocked service dependencies:
- Purchase transaction endpoints
- Purchase transaction item endpoints
- Request/response schema validation
- Error handling and HTTP status codes
- Authentication and authorization (when implemented)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4
from typing import Dict, Any, List

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from src.api.v1.schemas.purchase_transaction_schemas import (
    PurchaseTransactionCreateSchema,
    PurchaseTransactionCreateWithItemsSchema,
    PurchaseTransactionUpdateSchema,
    PurchaseTransactionResponseSchema,
    PurchaseTransactionWithItemsResponseSchema,
    PurchaseTransactionListResponseSchema,
    PurchaseTransactionSearchSchema,
    PurchaseTransactionStatisticsSchema,
    PurchaseTransactionItemCreateSchema,
    PurchaseTransactionItemUpdateSchema,
    PurchaseTransactionItemResponseSchema,
    PurchaseTransactionItemSummarySchema,
    BulkCreateItemsSchema,
    BulkCreateItemsResponseSchema
)

from src.domain.entities.purchase_transaction import PurchaseTransaction
from src.domain.entities.purchase_transaction_item import PurchaseTransactionItem


class TestPurchaseTransactionSchemas:
    """Test purchase transaction Pydantic schemas."""
    
    def test_purchase_transaction_create_schema_valid(self):
        """Test valid purchase transaction creation schema."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        data = {
            "transaction_date": transaction_date,
            "vendor_id": vendor_id,
            "purchase_order_number": "PO-001",
            "remarks": "Test transaction",
            "created_by": "test_user"
        }
        
        schema = PurchaseTransactionCreateSchema(**data)
        
        assert schema.transaction_date == transaction_date
        assert schema.vendor_id == vendor_id
        assert schema.purchase_order_number == "PO-001"
        assert schema.remarks == "Test transaction"
        assert schema.created_by == "test_user"
    
    def test_purchase_transaction_create_schema_future_date_validation(self):
        """Test transaction date validation for future dates."""
        vendor_id = str(uuid4())
        future_date = date(2030, 12, 31)
        
        data = {
            "transaction_date": future_date,
            "vendor_id": vendor_id
        }
        
        with pytest.raises(ValidationError, match="Transaction date cannot be in the future"):
            PurchaseTransactionCreateSchema(**data)
    
    def test_purchase_transaction_create_schema_missing_required_fields(self):
        """Test schema validation with missing required fields."""
        # Missing vendor_id
        with pytest.raises(ValidationError):
            PurchaseTransactionCreateSchema(transaction_date=date.today())
        
        # Missing transaction_date
        with pytest.raises(ValidationError):
            PurchaseTransactionCreateSchema(vendor_id=str(uuid4()))
    
    def test_purchase_transaction_item_create_schema_valid(self):
        """Test valid purchase transaction item creation schema."""
        item_master_id = str(uuid4())
        warehouse_id = str(uuid4())
        
        data = {
            "item_master_id": item_master_id,
            "quantity": 5,
            "unit_price": Decimal("100.00"),
            "warehouse_id": warehouse_id,
            "serial_number": ["SN001", "SN002", "SN003", "SN004", "SN005"],
            "discount": Decimal("50.00"),
            "tax_amount": Decimal("35.00"),
            "remarks": "Test item",
            "warranty_period_type": "MONTHS",
            "warranty_period": 12
        }
        
        schema = PurchaseTransactionItemCreateSchema(**data)
        
        assert schema.item_master_id == item_master_id
        assert schema.quantity == 5
        assert schema.unit_price == Decimal("100.00")
        assert schema.warehouse_id == warehouse_id
        assert schema.serial_number == ["SN001", "SN002", "SN003", "SN004", "SN005"]
        assert schema.discount == Decimal("50.00")
        assert schema.tax_amount == Decimal("35.00")
        assert schema.remarks == "Test item"
        assert schema.warranty_period_type == "MONTHS"
        assert schema.warranty_period == 12
    
    def test_purchase_transaction_item_create_schema_negative_values_validation(self):
        """Test item schema validation for negative values."""
        item_master_id = str(uuid4())
        
        # Negative quantity
        with pytest.raises(ValidationError, match="ensure this value is greater than 0"):
            PurchaseTransactionItemCreateSchema(
                item_master_id=item_master_id,
                quantity=0,  # Invalid
                unit_price=Decimal("100.00")
            )
        
        # Negative unit price
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            PurchaseTransactionItemCreateSchema(
                item_master_id=item_master_id,
                quantity=1,
                unit_price=Decimal("-50.00")  # Invalid
            )
        
        # Negative discount
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            PurchaseTransactionItemCreateSchema(
                item_master_id=item_master_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                discount=Decimal("-10.00")  # Invalid
            )
    
    def test_purchase_transaction_item_warranty_validation(self):
        """Test warranty period validation."""
        item_master_id = str(uuid4())
        
        # Invalid warranty period type
        with pytest.raises(ValidationError, match="Warranty period type must be DAYS, MONTHS, or YEARS"):
            PurchaseTransactionItemCreateSchema(
                item_master_id=item_master_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period_type="INVALID",
                warranty_period=12
            )
        
        # Warranty type without period
        with pytest.raises(ValidationError, match="Both warranty period type and warranty period must be provided together"):
            PurchaseTransactionItemCreateSchema(
                item_master_id=item_master_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period_type="MONTHS"
                # Missing warranty_period
            )
        
        # Warranty period without type
        with pytest.raises(ValidationError, match="Both warranty period type and warranty period must be provided together"):
            PurchaseTransactionItemCreateSchema(
                item_master_id=item_master_id,
                quantity=1,
                unit_price=Decimal("100.00"),
                warranty_period=12
                # Missing warranty_period_type
            )
    
    def test_purchase_transaction_create_with_items_schema_valid(self):
        """Test valid purchase transaction with items creation schema."""
        vendor_id = str(uuid4())
        item_master_id = str(uuid4())
        transaction_date = date.today()
        
        items = [
            {
                "item_master_id": item_master_id,
                "quantity": 2,
                "unit_price": "150.00"
            }
        ]
        
        data = {
            "transaction_date": transaction_date,
            "vendor_id": vendor_id,
            "items": items,
            "purchase_order_number": "PO-002",
            "remarks": "Transaction with items"
        }
        
        schema = PurchaseTransactionCreateWithItemsSchema(**data)
        
        assert schema.transaction_date == transaction_date
        assert schema.vendor_id == vendor_id
        assert len(schema.items) == 1
        assert schema.items[0].item_master_id == item_master_id
        assert schema.items[0].quantity == 2
        assert schema.items[0].unit_price == Decimal("150.00")
    
    def test_purchase_transaction_create_with_items_schema_empty_items_validation(self):
        """Test schema validation with empty items list."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        data = {
            "transaction_date": transaction_date,
            "vendor_id": vendor_id,
            "items": []  # Empty items list should be invalid
        }
        
        with pytest.raises(ValidationError, match="ensure this value has at least 1 items"):
            PurchaseTransactionCreateWithItemsSchema(**data)
    
    def test_purchase_transaction_update_schema_valid(self):
        """Test valid purchase transaction update schema."""
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        data = {
            "vendor_id": vendor_id,
            "transaction_date": transaction_date,
            "purchase_order_number": "PO-UPDATED",
            "remarks": "Updated remarks"
        }
        
        schema = PurchaseTransactionUpdateSchema(**data)
        
        assert schema.vendor_id == vendor_id
        assert schema.transaction_date == transaction_date
        assert schema.purchase_order_number == "PO-UPDATED"
        assert schema.remarks == "Updated remarks"
    
    def test_purchase_transaction_update_schema_all_optional(self):
        """Test update schema with all fields optional."""
        # Should be valid with no fields
        schema = PurchaseTransactionUpdateSchema()
        
        assert schema.vendor_id is None
        assert schema.transaction_date is None
        assert schema.purchase_order_number is None
        assert schema.remarks is None
    
    def test_purchase_transaction_response_schema(self):
        """Test purchase transaction response schema."""
        transaction_id = uuid4()
        vendor_id = str(uuid4())
        transaction_date = date.today()
        created_at = datetime.now(timezone.utc)
        
        data = {
            "id": transaction_id,
            "transaction_id": "PUR-001",
            "transaction_date": transaction_date,
            "vendor_id": vendor_id,
            "total_amount": Decimal("500.00"),
            "grand_total": Decimal("525.00"),
            "purchase_order_number": "PO-001",
            "remarks": "Response test",
            "created_at": created_at,
            "updated_at": created_at,
            "created_by": "test_user",
            "is_active": True
        }
        
        schema = PurchaseTransactionResponseSchema(**data)
        
        assert schema.id == transaction_id
        assert schema.transaction_id == "PUR-001"
        assert schema.transaction_date == transaction_date
        assert schema.vendor_id == vendor_id
        assert schema.total_amount == Decimal("500.00")
        assert schema.grand_total == Decimal("525.00")
    
    def test_purchase_transaction_search_schema_valid(self):
        """Test purchase transaction search schema."""
        vendor_id = str(uuid4())
        
        data = {
            "query": "test search",
            "vendor_id": vendor_id,
            "limit": 50
        }
        
        schema = PurchaseTransactionSearchSchema(**data)
        
        assert schema.query == "test search"
        assert schema.vendor_id == vendor_id
        assert schema.limit == 50
    
    def test_purchase_transaction_search_schema_empty_query_validation(self):
        """Test search schema with empty query."""
        with pytest.raises(ValidationError, match="ensure this value has at least 1 characters"):
            PurchaseTransactionSearchSchema(query="")
    
    def test_bulk_create_items_schema_valid(self):
        """Test bulk create items schema."""
        item_master_id = str(uuid4())
        
        items = [
            {
                "item_master_id": item_master_id,
                "quantity": 1,
                "unit_price": "100.00"
            },
            {
                "item_master_id": item_master_id,
                "quantity": 2,
                "unit_price": "150.00"
            }
        ]
        
        data = {"items": items}
        schema = BulkCreateItemsSchema(**data)
        
        assert len(schema.items) == 2
        assert schema.items[0].quantity == 1
        assert schema.items[1].quantity == 2
    
    def test_bulk_create_items_schema_empty_items_validation(self):
        """Test bulk create items schema with empty items."""
        with pytest.raises(ValidationError, match="ensure this value has at least 1 items"):
            BulkCreateItemsSchema(items=[])


class TestPurchaseTransactionEndpoints:
    """Test purchase transaction API endpoints."""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock purchase transaction service."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_get_service(self, mock_service):
        """Mock the get_purchase_transaction_service dependency."""
        with patch('src.api.v1.endpoints.purchase_transactions.get_purchase_transaction_service') as mock:
            mock.return_value = mock_service
            yield mock, mock_service
    
    @pytest.mark.asyncio
    async def test_create_transaction_success(self, mock_get_service):
        """Test successful transaction creation endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        # Setup test data
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        request_data = {
            "transaction_date": transaction_date.isoformat(),
            "vendor_id": str(vendor_id),
            "purchase_order_number": "PO-001",
            "remarks": "Test transaction",
            "created_by": "test_user"
        }
        
        # Mock service response
        mock_transaction = MagicMock()
        mock_transaction.id = uuid4()
        mock_transaction.transaction_id = "PUR-001"
        mock_transaction.transaction_date = transaction_date
        mock_transaction.vendor_id = vendor_id
        mock_transaction.total_amount = Decimal("0.00")
        mock_transaction.grand_total = Decimal("0.00")
        mock_transaction.purchase_order_number = "PO-001"
        mock_transaction.remarks = "Test transaction"
        mock_transaction.created_at = datetime.now(timezone.utc)
        mock_transaction.updated_at = datetime.now(timezone.utc)
        mock_transaction.created_by = "test_user"
        mock_transaction.is_active = True
        
        mock_service.create_transaction.return_value = mock_transaction
        
        # Import and test endpoint
        from src.api.v1.endpoints.purchase_transactions import create_transaction
        
        # Create schema object
        schema = PurchaseTransactionCreateSchema(**request_data)
        
        # Execute endpoint
        result = await create_transaction(schema, mock_service)
        
        # Verify service call
        mock_service.create_transaction.assert_called_once_with(
            vendor_id=vendor_id,
            transaction_date=transaction_date,
            purchase_order_number="PO-001",
            remarks="Test transaction",
            created_by="test_user"
        )
        
        # Verify response
        assert "transaction" in result
        assert "message" in result
        assert result["message"] == "Purchase transaction created successfully"
    
    @pytest.mark.asyncio
    async def test_create_transaction_service_error(self, mock_get_service):
        """Test transaction creation with service error."""
        mock_get_dep, mock_service = mock_get_service
        
        vendor_id = str(uuid4())
        transaction_date = date.today()
        
        request_data = {
            "transaction_date": transaction_date.isoformat(),
            "vendor_id": str(vendor_id)
        }
        
        # Mock service error
        mock_service.create_transaction.side_effect = ValueError("Vendor not found")
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import create_transaction
        
        # Create schema object
        schema = PurchaseTransactionCreateSchema(**request_data)
        
        # Execute endpoint and expect error
        with pytest.raises(HTTPException) as exc_info:
            await create_transaction(schema, mock_service)
        
        assert exc_info.value.status_code == 400
        assert "Vendor not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_transaction_with_items_success(self, mock_get_service):
        """Test successful transaction creation with items endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        # Setup test data
        vendor_id = str(uuid4())
        item_master_id = str(uuid4())
        transaction_date = date.today()
        
        request_data = {
            "transaction_date": transaction_date.isoformat(),
            "vendor_id": str(vendor_id),
            "items": [
                {
                    "item_master_id": str(item_master_id),
                    "quantity": 2,
                    "unit_price": "100.00"
                }
            ]
        }
        
        # Mock service response
        mock_transaction = MagicMock()
        mock_transaction.id = uuid4()
        mock_transaction.transaction_id = "PUR-002"
        mock_transaction.total_amount = Decimal("200.00")
        mock_transaction.grand_total = Decimal("200.00")
        
        mock_service.create_transaction_with_items.return_value = mock_transaction
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import create_transaction_with_items
        
        # Create schema object
        schema = PurchaseTransactionCreateWithItemsSchema(**request_data)
        
        # Execute endpoint
        result = await create_transaction_with_items(schema, mock_service)
        
        # Verify service call
        mock_service.create_transaction_with_items.assert_called_once()
        call_args = mock_service.create_transaction_with_items.call_args
        assert call_args.kwargs["vendor_id"] == vendor_id
        assert call_args.kwargs["transaction_date"] == transaction_date
        assert len(call_args.kwargs["items"]) == 1
        
        # Verify response
        assert "transaction" in result
        assert "message" in result
        assert result["message"] == "Purchase transaction with items created successfully"
    
    @pytest.mark.asyncio
    async def test_get_transactions_success(self, mock_get_service):
        """Test successful get transactions endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        # Mock service response
        mock_transactions = [MagicMock(), MagicMock()]
        for i, mock_transaction in enumerate(mock_transactions):
            mock_transaction.id = uuid4()
            mock_transaction.transaction_id = f"PUR-{i+1:03d}"
            mock_transaction.transaction_date = date.today()
            mock_transaction.vendor_id = uuid4()
            mock_transaction.total_amount = Decimal(f"{(i+1)*100}.00")
            mock_transaction.grand_total = Decimal(f"{(i+1)*105}.00")
            mock_transaction.purchase_order_number = None
            mock_transaction.remarks = None
            mock_transaction.created_at = datetime.now(timezone.utc)
            mock_transaction.updated_at = datetime.now(timezone.utc)
            mock_transaction.created_by = "test_user"
            mock_transaction.is_active = True
        
        list_result = {
            "transactions": mock_transactions,
            "total": 25,
            "page": 1,
            "page_size": 50,
            "total_pages": 1
        }
        mock_service.list_transactions.return_value = list_result
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transactions
        
        # Execute endpoint
        result = await get_transactions(service=mock_service)
        
        # Verify service call
        mock_service.list_transactions.assert_called_once_with(
            page=1,
            page_size=50,
            vendor_id=None,
            date_from=None,
            date_to=None,
            purchase_order_number=None,
            sort_by=None,
            sort_desc=True
        )
        
        # Verify response
        assert len(result.transactions) == 2
        assert result.total == 25
        assert result.page == 1
        assert result.page_size == 50
        assert result.total_pages == 1
    
    @pytest.mark.asyncio
    async def test_get_transactions_with_filters(self, mock_get_service):
        """Test get transactions endpoint with filters."""
        mock_get_dep, mock_service = mock_get_service
        
        vendor_id = str(uuid4())
        
        # Mock service response
        list_result = {
            "transactions": [],
            "total": 0,
            "page": 2,
            "page_size": 25,
            "total_pages": 0
        }
        mock_service.list_transactions.return_value = list_result
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transactions
        
        # Execute endpoint with filters
        result = await get_transactions(
            page=2,
            page_size=25,
            vendor_id=vendor_id,
            date_from="2024-01-01",
            date_to="2024-12-31",
            purchase_order_number="PO-",
            sort_by="transaction_date",
            sort_desc=False,
            service=mock_service
        )
        
        # Verify service call with filters
        mock_service.list_transactions.assert_called_once()
        call_args = mock_service.list_transactions.call_args
        assert call_args.kwargs["page"] == 2
        assert call_args.kwargs["page_size"] == 25
        assert call_args.kwargs["vendor_id"] == vendor_id
        assert call_args.kwargs["date_from"] == date(2024, 1, 1)
        assert call_args.kwargs["date_to"] == date(2024, 12, 31)
        assert call_args.kwargs["purchase_order_number"] == "PO-"
        assert call_args.kwargs["sort_by"] == "transaction_date"
        assert call_args.kwargs["sort_desc"] is False
    
    @pytest.mark.asyncio
    async def test_get_transaction_success(self, mock_get_service):
        """Test successful get single transaction endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        
        # Mock service response
        mock_transaction = MagicMock()
        mock_transaction.id = transaction_id
        mock_transaction.transaction_id = "PUR-001"
        mock_transaction.transaction_date = date.today()
        mock_transaction.vendor_id = uuid4()
        mock_transaction.total_amount = Decimal("300.00")
        mock_transaction.grand_total = Decimal("315.00")
        mock_transaction.purchase_order_number = "PO-001"
        mock_transaction.remarks = "Test transaction"
        mock_transaction.created_at = datetime.now(timezone.utc)
        mock_transaction.updated_at = datetime.now(timezone.utc)
        mock_transaction.created_by = "test_user"
        mock_transaction.is_active = True
        
        mock_items = [MagicMock(), MagicMock()]
        for i, mock_item in enumerate(mock_items):
            mock_item.id = uuid4()
            mock_item.transaction_id = transaction_id
            mock_item.inventory_item_id = uuid4()
            mock_item.warehouse_id = uuid4()
            mock_item.quantity = i + 1
            mock_item.unit_price = Decimal("150.00")
            mock_item.discount = Decimal("0.00")
            mock_item.tax_amount = Decimal("15.00")
            mock_item.total_price = Decimal(f"{(i+1)*165}.00")
            mock_item.serial_number = [f"SN{i+1:03d}"]
            mock_item.remarks = None
            mock_item.warranty_period_type = None
            mock_item.warranty_period = None
            mock_item.created_at = datetime.now(timezone.utc)
            mock_item.updated_at = datetime.now(timezone.utc)
            mock_item.created_by = "test_user"
            mock_item.is_active = True
        
        mock_summary = {
            "total_items": 2,
            "total_quantity": 3,
            "total_amount": 315.00,
            "total_discount": 0.00,
            "total_tax": 30.00,
            "average_unit_price": 150.00,
            "items_with_warranty": 0,
            "items_with_serial_numbers": 2
        }
        
        transaction_with_items = {
            "transaction": mock_transaction,
            "items": mock_items,
            "item_summary": mock_summary
        }
        mock_service.get_transaction_with_items.return_value = transaction_with_items
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction
        
        # Execute endpoint
        result = await get_transaction(transaction_id, mock_service)
        
        # Verify service call
        mock_service.get_transaction_with_items.assert_called_once_with(transaction_id)
        
        # Verify response
        assert result.id == transaction_id
        assert result.transaction_id == "PUR-001"
        assert len(result.items) == 2
        assert result.item_summary is not None
    
    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, mock_get_service):
        """Test get transaction endpoint when transaction not found."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        
        # Mock service response
        mock_service.get_transaction_with_items.return_value = None
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction
        
        # Execute endpoint and expect error
        with pytest.raises(HTTPException) as exc_info:
            await get_transaction(transaction_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Purchase transaction not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_transaction_success(self, mock_get_service):
        """Test successful update transaction endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        vendor_id = str(uuid4())
        
        request_data = {
            "vendor_id": str(vendor_id),
            "transaction_date": date.today().isoformat(),
            "purchase_order_number": "PO-UPDATED",
            "remarks": "Updated remarks"
        }
        
        # Mock service response
        mock_transaction = MagicMock()
        mock_transaction.id = transaction_id
        mock_transaction.vendor_id = vendor_id
        mock_transaction.purchase_order_number = "PO-UPDATED"
        mock_transaction.remarks = "Updated remarks"
        
        mock_service.update_transaction.return_value = mock_transaction
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import update_transaction
        
        # Create schema object
        schema = PurchaseTransactionUpdateSchema(**request_data)
        
        # Execute endpoint
        result = await update_transaction(transaction_id, schema, mock_service)
        
        # Verify service call
        mock_service.update_transaction.assert_called_once_with(
            transaction_id=transaction_id,
            vendor_id=vendor_id,
            transaction_date=date.today(),
            purchase_order_number="PO-UPDATED",
            remarks="Updated remarks"
        )
        
        # Verify response
        assert "transaction" in result
        assert "message" in result
        assert result["message"] == "Purchase transaction updated successfully"
    
    @pytest.mark.asyncio
    async def test_delete_transaction_success(self, mock_get_service):
        """Test successful delete transaction endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        
        # Mock service response
        mock_service.delete_transaction.return_value = True
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import delete_transaction
        
        # Execute endpoint
        result = await delete_transaction(transaction_id, mock_service)
        
        # Verify service call
        mock_service.delete_transaction.assert_called_once_with(transaction_id)
        
        # Verify response
        assert result["message"] == "Purchase transaction deleted successfully"
        assert result["transaction_id"] == str(transaction_id)
    
    @pytest.mark.asyncio
    async def test_delete_transaction_not_found(self, mock_get_service):
        """Test delete transaction endpoint when transaction not found."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        
        # Mock service response
        mock_service.delete_transaction.return_value = False
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import delete_transaction
        
        # Execute endpoint and expect error
        with pytest.raises(HTTPException) as exc_info:
            await delete_transaction(transaction_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Purchase transaction not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_search_transactions_success(self, mock_get_service):
        """Test successful search transactions endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        vendor_id = str(uuid4())
        
        request_data = {
            "query": "test search",
            "vendor_id": str(vendor_id),
            "limit": 50
        }
        
        # Mock service response
        mock_transactions = [MagicMock()]
        mock_service.search_transactions.return_value = mock_transactions
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import search_transactions
        
        # Create schema object
        schema = PurchaseTransactionSearchSchema(**request_data)
        
        # Execute endpoint
        result = await search_transactions(schema, mock_service)
        
        # Verify service call
        mock_service.search_transactions.assert_called_once_with(
            query="test search",
            vendor_id=vendor_id
        )
        
        # Verify response
        assert len(result.transactions) == 1
        assert result.total == 1
        assert result.page == 1
        assert result.page_size == 1
        assert result.total_pages == 1
    
    @pytest.mark.asyncio
    async def test_get_transaction_statistics_success(self, mock_get_service):
        """Test successful get transaction statistics endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        # Mock service response
        mock_stats = {
            "total_amount": Decimal("50000.00"),
            "total_transactions": 200,
            "recent_amount": Decimal("15000.00"),
            "recent_transactions": 60
        }
        mock_service.get_statistics.return_value = mock_stats
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction_statistics
        
        # Execute endpoint
        result = await get_transaction_statistics(mock_service)
        
        # Verify service call
        mock_service.get_statistics.assert_called_once()
        
        # Verify response
        assert result.total_amount == Decimal("50000.00")
        assert result.total_transactions == 200
        assert result.recent_amount == Decimal("15000.00")
        assert result.recent_transactions == 60


class TestPurchaseTransactionItemEndpoints:
    """Test purchase transaction item API endpoints."""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock purchase transaction service."""
        return AsyncMock()
    
    @pytest.fixture
    def mock_get_service(self, mock_service):
        """Mock the get_purchase_transaction_service dependency."""
        with patch('src.api.v1.endpoints.purchase_transactions.get_purchase_transaction_service') as mock:
            mock.return_value = mock_service
            yield mock, mock_service
    
    @pytest.mark.asyncio
    async def test_create_transaction_item_success(self, mock_get_service):
        """Test successful transaction item creation endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_master_id = str(uuid4())
        
        request_data = {
            "item_master_id": str(item_master_id),
            "quantity": 3,
            "unit_price": "120.00",
            "discount": "12.00",
            "tax_amount": "18.00",
            "remarks": "Test item"
        }
        
        # Mock service response
        mock_item = MagicMock()
        mock_item.id = uuid4()
        mock_item.transaction_id = transaction_id
        mock_item.inventory_item_id = item_master_id
        mock_item.quantity = 3
        mock_item.unit_price = Decimal("120.00")
        mock_item.discount = Decimal("12.00")
        mock_item.tax_amount = Decimal("18.00")
        mock_item.total_price = Decimal("366.00")  # (3 * 120.00) - 12.00 + 18.00
        mock_item.remarks = "Test item"
        
        mock_service.create_item.return_value = mock_item
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import create_transaction_item
        
        # Create schema object
        schema = PurchaseTransactionItemCreateSchema(**request_data)
        
        # Execute endpoint
        result = await create_transaction_item(transaction_id, schema, mock_service)
        
        # Verify service call
        mock_service.create_item.assert_called_once_with(
            transaction_id=transaction_id,
            item_master_id=item_master_id,
            quantity=3,
            unit_price=Decimal("120.00"),
            warehouse_id=None,
            serial_number=None,
            discount=Decimal("12.00"),
            tax_amount=Decimal("18.00"),
            remarks="Test item",
            warranty_period_type=None,
            warranty_period=None
        )
        
        # Verify response
        assert "item" in result
        assert "message" in result
        assert result["message"] == "Transaction item created successfully"
    
    @pytest.mark.asyncio
    async def test_bulk_create_transaction_items_success(self, mock_get_service):
        """Test successful bulk transaction items creation endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_master_id1 = uuid4()
        item_master_id2 = uuid4()
        
        request_data = {
            "items": [
                {
                    "item_master_id": str(item_master_id1),
                    "quantity": 1,
                    "unit_price": "100.00"
                },
                {
                    "item_master_id": str(item_master_id2),
                    "quantity": 2,
                    "unit_price": "150.00"
                }
            ]
        }
        
        # Mock service response
        mock_items = [MagicMock(), MagicMock()]
        mock_service.bulk_create_items.return_value = mock_items
        
        # Mock updated transaction
        mock_transaction = MagicMock()
        mock_transaction.total_amount = Decimal("400.00")
        mock_transaction.grand_total = Decimal("400.00")
        mock_service.get_transaction.return_value = mock_transaction
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import bulk_create_transaction_items
        
        # Create schema object
        schema = BulkCreateItemsSchema(**request_data)
        
        # Execute endpoint
        result = await bulk_create_transaction_items(transaction_id, schema, mock_service)
        
        # Verify service call
        mock_service.bulk_create_items.assert_called_once()
        call_args = mock_service.bulk_create_items.call_args
        assert call_args.kwargs["transaction_id"] == transaction_id
        assert len(call_args.kwargs["items_data"]) == 2
        
        # Verify response
        assert len(result.created_items) == 2
        assert result.total_created == 2
        assert result.total_requested == 2
        assert result.transaction_id == transaction_id
        assert result.updated_totals["total_amount"] == Decimal("400.00")
    
    @pytest.mark.asyncio
    async def test_get_transaction_items_success(self, mock_get_service):
        """Test successful get transaction items endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        
        # Mock service response
        mock_items = [MagicMock(), MagicMock()]
        items_result = {
            "items": mock_items,
            "total": 15,
            "page": 1,
            "page_size": 50,
            "total_pages": 1
        }
        mock_service.get_items_by_transaction.return_value = items_result
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction_items
        
        # Execute endpoint
        result = await get_transaction_items(transaction_id, service=mock_service)
        
        # Verify service call
        mock_service.get_items_by_transaction.assert_called_once_with(transaction_id, 1, 50)
        
        # Verify response
        assert len(result["items"]) == 2
        assert result["total"] == 15
        assert result["page"] == 1
        assert result["page_size"] == 50
        assert result["total_pages"] == 1
    
    @pytest.mark.asyncio
    async def test_get_transaction_item_success(self, mock_get_service):
        """Test successful get single transaction item endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_id = uuid4()
        
        # Mock service response
        mock_item = MagicMock()
        mock_item.id = item_id
        mock_item.transaction_id = transaction_id
        mock_item.inventory_item_id = uuid4()
        mock_item.quantity = 2
        mock_item.unit_price = Decimal("75.00")
        mock_item.total_price = Decimal("150.00")
        
        mock_service.get_item.return_value = mock_item
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction_item
        
        # Execute endpoint
        result = await get_transaction_item(transaction_id, item_id, mock_service)
        
        # Verify service call
        mock_service.get_item.assert_called_once_with(item_id)
        
        # Verify response
        assert result.id == item_id
        assert result.transaction_id == transaction_id
    
    @pytest.mark.asyncio
    async def test_get_transaction_item_not_found(self, mock_get_service):
        """Test get transaction item endpoint when item not found."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_id = uuid4()
        
        # Mock service response
        mock_service.get_item.return_value = None
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction_item
        
        # Execute endpoint and expect error
        with pytest.raises(HTTPException) as exc_info:
            await get_transaction_item(transaction_id, item_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Transaction item not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_transaction_item_wrong_transaction(self, mock_get_service):
        """Test get transaction item endpoint when item belongs to different transaction."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_id = uuid4()
        different_transaction_id = uuid4()
        
        # Mock service response with item from different transaction
        mock_item = MagicMock()
        mock_item.id = item_id
        mock_item.transaction_id = different_transaction_id  # Different transaction
        
        mock_service.get_item.return_value = mock_item
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import get_transaction_item
        
        # Execute endpoint and expect error
        with pytest.raises(HTTPException) as exc_info:
            await get_transaction_item(transaction_id, item_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Transaction item not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_transaction_item_success(self, mock_get_service):
        """Test successful update transaction item endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_id = uuid4()
        
        request_data = {
            "unit_price": "130.00",
            "discount": "13.00",
            "tax_amount": "19.50",
            "remarks": "Updated item"
        }
        
        # Mock service response
        mock_item = MagicMock()
        mock_item.id = item_id
        mock_item.unit_price = Decimal("130.00")
        mock_item.discount = Decimal("13.00")
        mock_item.tax_amount = Decimal("19.50")
        mock_item.remarks = "Updated item"
        
        mock_service.update_item.return_value = mock_item
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import update_transaction_item
        
        # Create schema object
        schema = PurchaseTransactionItemUpdateSchema(**request_data)
        
        # Execute endpoint
        result = await update_transaction_item(transaction_id, item_id, schema, mock_service)
        
        # Verify service call
        mock_service.update_item.assert_called_once_with(
            item_id=item_id,
            unit_price=Decimal("130.00"),
            discount=Decimal("13.00"),
            tax_amount=Decimal("19.50"),
            remarks="Updated item",
            warranty_period_type=None,
            warranty_period=None
        )
        
        # Verify response
        assert "item" in result
        assert "message" in result
        assert result["message"] == "Transaction item updated successfully"
    
    @pytest.mark.asyncio
    async def test_delete_transaction_item_success(self, mock_get_service):
        """Test successful delete transaction item endpoint."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_id = uuid4()
        
        # Mock service response
        mock_service.delete_item.return_value = True
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import delete_transaction_item
        
        # Execute endpoint
        result = await delete_transaction_item(transaction_id, item_id, mock_service)
        
        # Verify service call
        mock_service.delete_item.assert_called_once_with(item_id)
        
        # Verify response
        assert result["message"] == "Transaction item deleted successfully"
        assert result["item_id"] == str(item_id)
    
    @pytest.mark.asyncio
    async def test_delete_transaction_item_not_found(self, mock_get_service):
        """Test delete transaction item endpoint when item not found."""
        mock_get_dep, mock_service = mock_get_service
        
        transaction_id = uuid4()
        item_id = uuid4()
        
        # Mock service response
        mock_service.delete_item.return_value = False
        
        # Import endpoint
        from src.api.v1.endpoints.purchase_transactions import delete_transaction_item
        
        # Execute endpoint and expect error
        with pytest.raises(HTTPException) as exc_info:
            await delete_transaction_item(transaction_id, item_id, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "Transaction item not found" in str(exc_info.value.detail)