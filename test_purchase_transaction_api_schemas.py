#!/usr/bin/env python3
"""
Test Purchase Transaction API Schemas for PRD Compliance

This script tests the API schemas to ensure they match PRD requirements.
"""

import sys
import os
from datetime import date
from decimal import Decimal
from uuid import uuid4

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_purchase_transaction_api_schemas():
    """Test API schemas for PRD compliance."""
    
    print("🔍 Testing Purchase Transaction API Schemas for PRD Compliance\n")
    
    try:
        # Test 1: Schema Imports
        print("📋 Test 1: Schema Imports and Structure")
        from src.api.v1.schemas.purchase_transaction_schemas import (
            PurchaseTransactionCreateSchema,
            PurchaseTransactionCreateWithItemsSchema,
            PurchaseTransactionUpdateSchema,
            PurchaseTransactionStatusUpdateSchema,
            PurchaseTransactionResponseSchema,
            PurchaseTransactionWithItemsResponseSchema,
            PurchaseTransactionListResponseSchema,
            PurchaseTransactionFiltersSchema,
            PurchaseTransactionSearchSchema,
            PurchaseTransactionStatisticsSchema,
            PurchaseTransactionItemCreateSchema,
            PurchaseTransactionItemUpdateSchema,
            PurchaseTransactionItemResponseSchema,
            PurchaseTransactionItemSummarySchema,
            BulkCreateItemsSchema,
            BulkCreateItemsResponseSchema
        )
        print("✅ All required schemas imported successfully")
        
        # Test 2: Transaction Creation Schema
        print("\n📋 Test 2: Transaction Creation Schema Validation")
        vendor_id = uuid4()
        
        # Test valid transaction creation data
        valid_transaction_data = {
            "transaction_date": str(date.today()),
            "vendor_id": str(vendor_id),
            "purchase_order_number": "PO-001",
            "remarks": "Test transaction",
            "created_by": "test_user"
        }
        
        transaction_schema = PurchaseTransactionCreateSchema(**valid_transaction_data)
        assert transaction_schema.vendor_id == vendor_id
        assert transaction_schema.transaction_date == date.today()
        print("✅ Transaction creation schema validation works")
        
        # Test 3: Future Date Validation
        print("\n📋 Test 3: Future Date Validation")
        future_date_data = valid_transaction_data.copy()
        future_date_data["transaction_date"] = "2030-12-31"
        
        try:
            PurchaseTransactionCreateSchema(**future_date_data)
            assert False, "Should reject future dates"
        except ValueError as e:
            assert "future" in str(e), "Should mention future date in error"
            print("✅ Future date validation works correctly")
        
        # Test 4: Transaction Item Schema
        print("\n📋 Test 4: Transaction Item Schema Validation")
        item_master_id = uuid4()
        
        valid_item_data = {
            "item_master_id": str(item_master_id),
            "quantity": 5,
            "unit_price": "100.50",
            "discount": "10.00",
            "tax_amount": "15.25",
            "serial_number": ["SN001", "SN002", "SN003", "SN004", "SN005"],
            "warranty_period_type": "MONTHS",
            "warranty_period": 12
        }
        
        item_schema = PurchaseTransactionItemCreateSchema(**valid_item_data)
        assert item_schema.quantity == 5
        assert item_schema.unit_price == Decimal("100.50")
        assert len(item_schema.serial_number) == 5
        print("✅ Transaction item schema validation works")
        
        # Test 5: Warranty Period Validation
        print("\n📋 Test 5: Warranty Period Validation")
        
        # Test valid warranty types
        for warranty_type in ["DAYS", "MONTHS", "YEARS"]:
            warranty_data = valid_item_data.copy()
            warranty_data["warranty_period_type"] = warranty_type
            warranty_schema = PurchaseTransactionItemCreateSchema(**warranty_data)
            assert warranty_schema.warranty_period_type == warranty_type
        
        print("✅ Warranty period type validation works")
        
        # Test invalid warranty type
        try:
            invalid_warranty_data = valid_item_data.copy()
            invalid_warranty_data["warranty_period_type"] = "INVALID"
            PurchaseTransactionItemCreateSchema(**invalid_warranty_data)
            assert False, "Should reject invalid warranty type"
        except ValueError as e:
            print("✅ Invalid warranty type validation works")
        
        # Test 6: Transaction with Items Schema
        print("\n📋 Test 6: Transaction with Items Schema")
        
        transaction_with_items_data = {
            "transaction_date": str(date.today()),
            "vendor_id": str(vendor_id),
            "created_by": "test_user",
            "items": [
                {
                    "item_master_id": str(uuid4()),
                    "quantity": 2,
                    "unit_price": "50.00"
                },
                {
                    "item_master_id": str(uuid4()),
                    "quantity": 3,
                    "unit_price": "75.00",
                    "warranty_period_type": "YEARS",
                    "warranty_period": 2
                }
            ]
        }
        
        transaction_with_items = PurchaseTransactionCreateWithItemsSchema(**transaction_with_items_data)
        assert len(transaction_with_items.items) == 2
        assert transaction_with_items.items[1].warranty_period_type == "YEARS"
        print("✅ Transaction with items schema validation works")
        
        # Test 7: Status Update Schema
        print("\n📋 Test 7: Status Update Schema Validation")
        
        valid_statuses = ["DRAFT", "CONFIRMED", "PROCESSING", "RECEIVED", "COMPLETED", "CANCELLED"]
        
        for status in valid_statuses:
            status_schema = PurchaseTransactionStatusUpdateSchema(status=status)
            assert status_schema.status == status
        
        print("✅ Valid status update validation works")
        
        # Test invalid status
        try:
            PurchaseTransactionStatusUpdateSchema(status="INVALID_STATUS")
            assert False, "Should reject invalid status"
        except ValueError:
            print("✅ Invalid status validation works")
        
        # Test 8: Search and Filter Schemas
        print("\n📋 Test 8: Search and Filter Schema Validation")
        
        filter_data = {
            "page": 1,
            "page_size": 50,
            "vendor_id": str(vendor_id),
            "status": "CONFIRMED",
            "date_from": str(date.today()),
            "date_to": str(date.today()),
            "sort_by": "transaction_date",
            "sort_desc": True
        }
        
        filter_schema = PurchaseTransactionFiltersSchema(**filter_data)
        assert filter_schema.page == 1
        assert filter_schema.vendor_id == vendor_id
        print("✅ Filter schema validation works")
        
        search_data = {
            "query": "PO-001",
            "vendor_id": str(vendor_id),
            "status": "CONFIRMED",
            "limit": 10
        }
        
        search_schema = PurchaseTransactionSearchSchema(**search_data)
        assert search_schema.query == "PO-001"
        assert search_schema.limit == 10
        print("✅ Search schema validation works")
        
        # Test 9: Bulk Operations Schema
        print("\n📋 Test 9: Bulk Operations Schema Validation")
        
        bulk_items_data = {
            "items": [
                {
                    "item_master_id": str(uuid4()),
                    "quantity": 1,
                    "unit_price": "25.00"
                },
                {
                    "item_master_id": str(uuid4()),
                    "quantity": 2,
                    "unit_price": "30.00"
                }
            ]
        }
        
        bulk_schema = BulkCreateItemsSchema(**bulk_items_data)
        assert len(bulk_schema.items) == 2
        print("✅ Bulk operations schema validation works")
        
        # Test 10: Response Schemas Structure
        print("\n📋 Test 10: Response Schema Structure Validation")
        
        # Test that response schemas have the required fields
        response_fields = [
            'id', 'transaction_id', 'transaction_date', 'vendor_id', 
            'status', 'total_amount', 'grand_total', 'created_at', 'updated_at'
        ]
        
        # Get the field annotations from the schema
        response_schema_fields = PurchaseTransactionResponseSchema.model_fields.keys()
        
        for field in response_fields:
            assert field in response_schema_fields, f"Response schema missing field: {field}"
        
        print("✅ Response schema structure validation works")
        
        # Test 11: Data Type Validation
        print("\n📋 Test 11: Data Type Validation")
        
        # Test that Decimal fields work correctly
        item_with_decimals = PurchaseTransactionItemCreateSchema(
            item_master_id=str(uuid4()),
            quantity=1,
            unit_price="99.99",
            discount="5.50",
            tax_amount="12.34"
        )
        
        assert isinstance(item_with_decimals.unit_price, Decimal)
        assert item_with_decimals.unit_price == Decimal("99.99")
        print("✅ Decimal data type validation works")
        
        # Final Summary
        print("\n🎉 ALL API SCHEMA TESTS PASSED!")
        print("\n📊 Schema Validation Summary:")
        print("✅ Schema imports and structure")
        print("✅ Transaction creation validation")
        print("✅ Future date validation")
        print("✅ Transaction item validation")
        print("✅ Warranty period validation")
        print("✅ Transaction with items validation") 
        print("✅ Status update validation")
        print("✅ Search and filter validation")
        print("✅ Bulk operations validation")
        print("✅ Response schema structure")
        print("✅ Data type validation")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Schema test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_purchase_transaction_api_schemas()
    sys.exit(0 if success else 1)