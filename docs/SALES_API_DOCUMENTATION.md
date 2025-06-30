# Sales Module API Documentation

## Overview

The Sales Module provides comprehensive functionality for managing sales transactions and returns in the rental management system. This API follows RESTful conventions and returns JSON responses.

**Base URL**: `http://localhost:8000/api/v1`

## Table of Contents

1. [Sales Transactions API](#sales-transactions-api)
2. [Sales Returns API](#sales-returns-api)
3. [Common Schemas](#common-schemas)
4. [Error Handling](#error-handling)

---

## Sales Transactions API

### 1. Create Sales Transaction

Create a new sales transaction with items.

**Endpoint**: `POST /sales/transactions/`

**Request Schema**:
```json
{
  "customer_id": "uuid",
  "items": [
    {
      "inventory_item_master_id": "uuid",
      "warehouse_id": "uuid", 
      "quantity": "integer",
      "unit_price": "decimal",
      "discount_percentage": "decimal (optional)",
      "tax_rate": "decimal (optional)",
      "serial_numbers": ["string"] // for individually tracked items
    }
  ],
  "shipping_amount": "decimal (optional, default: 0.00)",
  "payment_terms": "string (optional, default: IMMEDIATE)",
  "shipping_address": "string (optional)",
  "billing_address": "string (optional)",
  "purchase_order_number": "string (optional)",
  "notes": "string (optional)",
  "customer_notes": "string (optional)"
}
```

**Example Request**:
```json
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": [
    {
      "inventory_item_master_id": "550e8400-e29b-41d4-a716-446655440001",
      "warehouse_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 2,
      "unit_price": "100.00",
      "discount_percentage": "10.0",
      "tax_rate": "8.5",
      "serial_numbers": ["SN001", "SN002"]
    },
    {
      "inventory_item_master_id": "550e8400-e29b-41d4-a716-446655440003",
      "warehouse_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 1,
      "unit_price": "50.00",
      "tax_rate": "8.5"
    }
  ],
  "shipping_amount": "25.00",
  "payment_terms": "NET_30",
  "shipping_address": "123 Main St, City, State 12345",
  "billing_address": "456 Business Ave, City, State 12345",
  "purchase_order_number": "PO-2024-001",
  "notes": "Rush delivery requested",
  "customer_notes": "Please call before delivery"
}
```

**Response** (`201 Created`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "transaction_id": "SO-2024-001",
  "invoice_number": "INV-2024-001",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "credit_limit": "5000.00"
  },
  "order_date": "2024-06-30T10:30:00Z",
  "delivery_date": null,
  "status": "DRAFT",
  "payment_status": "PENDING",
  "payment_terms": "NET_30",
  "payment_due_date": "2024-07-30",
  "subtotal": "230.00",
  "discount_amount": "20.00",
  "tax_amount": "17.85",
  "shipping_amount": "25.00",
  "grand_total": "252.85",
  "amount_paid": "0.00",
  "balance_due": "252.85",
  "shipping_address": "123 Main St, City, State 12345",
  "billing_address": "456 Business Ave, City, State 12345",
  "purchase_order_number": "PO-2024-001",
  "sales_person_id": null,
  "notes": "Rush delivery requested",
  "customer_notes": "Please call before delivery",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440020",
      "inventory_item_master_id": "550e8400-e29b-41d4-a716-446655440001",
      "inventory_item": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "MacBook Pro 16-inch",
        "sku": "MBP16-001"
      },
      "warehouse_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 2,
      "unit_price": "100.00",
      "discount_percentage": "10.0",
      "discount_amount": "20.00",
      "tax_rate": "8.5",
      "tax_amount": "15.30",
      "subtotal": "180.00",
      "total": "195.30",
      "serial_numbers": ["SN001", "SN002"]
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440021",
      "inventory_item_master_id": "550e8400-e29b-41d4-a716-446655440003",
      "inventory_item": {
        "id": "550e8400-e29b-41d4-a716-446655440003",
        "name": "Wireless Mouse",
        "sku": "MOUSE-001"
      },
      "warehouse_id": "550e8400-e29b-41d4-a716-446655440002",
      "quantity": 1,
      "unit_price": "50.00",
      "discount_percentage": "0.0",
      "discount_amount": "0.00",
      "tax_rate": "8.5",
      "tax_amount": "2.55",
      "subtotal": "50.00",
      "total": "52.55",
      "serial_numbers": []
    }
  ],
  "created_at": "2024-06-30T10:30:00Z",
  "updated_at": "2024-06-30T10:30:00Z",
  "is_active": true
}
```

### 2. Get Sales Transaction

Retrieve a specific sales transaction by ID.

**Endpoint**: `GET /sales/transactions/{transaction_id}`

**Path Parameters**:
- `transaction_id` (UUID): The transaction ID

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "transaction_id": "SO-2024-001",
  "invoice_number": "INV-2024-001",
  "customer_id": "550e8400-e29b-41d4-a716-446655440000",
  "customer": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "address": "123 Customer St",
    "city": "Customer City",
    "credit_limit": "5000.00"
  },
  "order_date": "2024-06-30T10:30:00Z",
  "delivery_date": null,
  "status": "CONFIRMED",
  "payment_status": "PENDING",
  "payment_terms": "NET_30",
  "payment_due_date": "2024-07-30",
  "subtotal": "230.00",
  "discount_amount": "20.00",
  "tax_amount": "17.85",
  "shipping_amount": "25.00",
  "grand_total": "252.85",
  "amount_paid": "0.00",
  "balance_due": "252.85",
  "shipping_address": "123 Main St, City, State 12345",
  "billing_address": "456 Business Ave, City, State 12345",
  "purchase_order_number": "PO-2024-001",
  "sales_person_id": null,
  "notes": "Rush delivery requested",
  "customer_notes": "Please call before delivery",
  "items": [
    // ... items array as shown in create response
  ],
  "created_at": "2024-06-30T10:30:00Z",
  "updated_at": "2024-06-30T10:35:00Z",
  "is_active": true
}
```

### 3. List Sales Transactions

Retrieve a list of sales transactions with optional filtering and pagination.

**Endpoint**: `GET /sales/transactions/`

**Query Parameters**:
- `customer_id` (UUID, optional): Filter by customer
- `status` (string, optional): Filter by status (`DRAFT`, `CONFIRMED`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`)
- `payment_status` (string, optional): Filter by payment status (`PENDING`, `PARTIAL`, `PAID`, `OVERDUE`, `REFUNDED`)
- `start_date` (ISO datetime, optional): Filter orders from this date
- `end_date` (ISO datetime, optional): Filter orders to this date
- `search` (string, optional): Search in transaction ID, invoice number, or notes
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 50): Maximum records to return
- `sort_by` (string, optional, default: "order_date"): Field to sort by
- `sort_desc` (boolean, optional, default: true): Sort in descending order

**Example Request**:
```
GET /sales/transactions/?customer_id=550e8400-e29b-41d4-a716-446655440000&status=CONFIRMED&limit=10
```

**Response** (`200 OK`):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "transaction_id": "SO-2024-001",
    "invoice_number": "INV-2024-001",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "customer_name": "John Doe",
    "order_date": "2024-06-30T10:30:00Z",
    "delivery_date": null,
    "status": "CONFIRMED",
    "payment_status": "PENDING",
    "payment_terms": "NET_30",
    "payment_due_date": "2024-07-30",
    "grand_total": "252.85",
    "amount_paid": "0.00",
    "balance_due": "252.85",
    "created_at": "2024-06-30T10:30:00Z",
    "updated_at": "2024-06-30T10:35:00Z"
  }
  // ... more transactions
]
```

### 4. Update Sales Transaction

Update a sales transaction (only certain fields can be updated based on status).

**Endpoint**: `PATCH /sales/transactions/{transaction_id}`

**Path Parameters**:
- `transaction_id` (UUID): The transaction ID

**Request Schema**:
```json
{
  "status": "string (optional)",
  "payment_status": "string (optional)",
  "delivery_date": "ISO datetime (optional)",
  "shipping_address": "string (optional)",
  "billing_address": "string (optional)",
  "notes": "string (optional)",
  "customer_notes": "string (optional)"
}
```

**Example Request**:
```json
{
  "status": "PROCESSING",
  "delivery_date": "2024-07-05T14:00:00Z",
  "notes": "Updated delivery date per customer request"
}
```

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "transaction_id": "SO-2024-001",
  "status": "PROCESSING",
  "delivery_date": "2024-07-05T14:00:00Z",
  "notes": "Updated delivery date per customer request",
  // ... other fields
  "updated_at": "2024-06-30T11:00:00Z"
}
```

### 5. Confirm Sales Transaction

Confirm a draft sales transaction.

**Endpoint**: `POST /sales/transactions/{transaction_id}/confirm`

**Path Parameters**:
- `transaction_id` (UUID): The transaction ID

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "transaction_id": "SO-2024-001",
  "status": "CONFIRMED",
  "payment_due_date": "2024-07-30",
  // ... other fields
  "updated_at": "2024-06-30T11:00:00Z"
}
```

### 6. Cancel Sales Transaction

Cancel a sales transaction.

**Endpoint**: `POST /sales/transactions/{transaction_id}/cancel`

**Request Schema**:
```json
{
  "reason": "string"
}
```

**Example Request**:
```json
{
  "reason": "Customer requested cancellation"
}
```

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "transaction_id": "SO-2024-001",
  "status": "CANCELLED",
  // ... other fields
  "updated_at": "2024-06-30T11:00:00Z"
}
```

### 7. Process Payment

Process a payment for a sales transaction.

**Endpoint**: `POST /sales/transactions/{transaction_id}/payment`

**Request Schema**:
```json
{
  "payment_amount": "decimal",
  "payment_method": "string (optional)",
  "reference_number": "string (optional)",
  "notes": "string (optional)"
}
```

**Example Request**:
```json
{
  "payment_amount": "252.85",
  "payment_method": "CREDIT_CARD",
  "reference_number": "CC-12345678",
  "notes": "Full payment received"
}
```

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "transaction_id": "SO-2024-001",
  "payment_status": "PAID",
  "amount_paid": "252.85",
  "balance_due": "0.00",
  // ... other fields
  "updated_at": "2024-06-30T11:00:00Z"
}
```

### 8. Get Overdue Transactions

Retrieve all overdue transactions.

**Endpoint**: `GET /sales/transactions/overdue`

**Response** (`200 OK`):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "transaction_id": "SO-2024-001",
    "customer_name": "John Doe",
    "payment_due_date": "2024-06-15",
    "days_overdue": 15,
    "grand_total": "252.85",
    "balance_due": "252.85",
    // ... other fields
  }
]
```

### 9. Get Sales Summary

Get sales summary statistics for a date range.

**Endpoint**: `GET /sales/transactions/summary`

**Query Parameters**:
- `start_date` (ISO datetime, required): Start date for summary
- `end_date` (ISO datetime, required): End date for summary

**Example Request**:
```
GET /sales/transactions/summary?start_date=2024-06-01T00:00:00Z&end_date=2024-06-30T23:59:59Z
```

**Response** (`200 OK`):
```json
{
  "period": {
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-30T23:59:59Z"
  },
  "total_sales": "15750.50",
  "total_orders": 25,
  "paid_amount": "12500.00",
  "pending_amount": "3250.50",
  "average_order_value": "630.02",
  "status_breakdown": {
    "DRAFT": 3,
    "CONFIRMED": 8,
    "PROCESSING": 5,
    "SHIPPED": 4,
    "DELIVERED": 3,
    "CANCELLED": 2
  },
  "payment_breakdown": {
    "PENDING": 8,
    "PARTIAL": 3,
    "PAID": 12,
    "OVERDUE": 2
  }
}
```

---

## Sales Returns API

### 1. Create Sales Return

Create a new sales return for returned items.

**Endpoint**: `POST /sales/returns/`

**Request Schema**:
```json
{
  "sales_transaction_id": "uuid",
  "reason": "string",
  "items": [
    {
      "sales_item_id": "uuid",
      "quantity": "integer",
      "condition": "string",
      "serial_numbers": ["string"] // for individually tracked items
    }
  ],
  "restocking_fee": "decimal (optional, default: 0.0)" // percentage (0-100)
}
```

**Example Request**:
```json
{
  "sales_transaction_id": "550e8400-e29b-41d4-a716-446655440010",
  "reason": "Customer not satisfied with product quality",
  "items": [
    {
      "sales_item_id": "550e8400-e29b-41d4-a716-446655440020",
      "quantity": 1,
      "condition": "GOOD",
      "serial_numbers": ["SN001"]
    }
  ],
  "restocking_fee": 10.0
}
```

**Response** (`201 Created`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "return_id": "RET-2024-001",
  "sales_transaction_id": "550e8400-e29b-41d4-a716-446655440010",
  "sales_transaction": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "transaction_id": "SO-2024-001",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "order_date": "2024-06-30T10:30:00Z",
    "grand_total": "252.85"
  },
  "return_date": "2024-07-05T14:30:00Z",
  "reason": "Customer not satisfied with product quality",
  "approved_by_id": null,
  "approved_by_name": null,
  "refund_amount": "97.65",
  "restocking_fee": "9.77",
  "net_refund_amount": "87.88",
  "is_approved": false,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440040",
      "sales_return_id": "550e8400-e29b-41d4-a716-446655440030",
      "sales_item_id": "550e8400-e29b-41d4-a716-446655440020",
      "sales_item": {
        "id": "550e8400-e29b-41d4-a716-446655440020",
        "inventory_item_master_id": "550e8400-e29b-41d4-a716-446655440001",
        "quantity": 2,
        "unit_price": "100.00",
        "total": "195.30"
      },
      "quantity": 1,
      "condition": "GOOD",
      "serial_numbers": ["SN001"],
      "is_resellable": true,
      "created_at": "2024-07-05T14:30:00Z"
    }
  ],
  "created_at": "2024-07-05T14:30:00Z",
  "updated_at": "2024-07-05T14:30:00Z",
  "is_active": true
}
```

### 2. Get Sales Return

Retrieve a specific sales return by ID.

**Endpoint**: `GET /sales/returns/{return_id}`

**Path Parameters**:
- `return_id` (UUID): The return ID

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "return_id": "RET-2024-001",
  "sales_transaction_id": "550e8400-e29b-41d4-a716-446655440010",
  "sales_transaction": {
    "id": "550e8400-e29b-41d4-a716-446655440010",
    "transaction_id": "SO-2024-001",
    "customer_id": "550e8400-e29b-41d4-a716-446655440000",
    "order_date": "2024-06-30T10:30:00Z",
    "grand_total": "252.85"
  },
  "return_date": "2024-07-05T14:30:00Z",
  "reason": "Customer not satisfied with product quality",
  "approved_by_id": "550e8400-e29b-41d4-a716-446655440050",
  "approved_by_name": "Manager Smith",
  "refund_amount": "97.65",
  "restocking_fee": "9.77",
  "net_refund_amount": "87.88",
  "is_approved": true,
  "items": [
    // ... items array as shown in create response
  ],
  "created_at": "2024-07-05T14:30:00Z",
  "updated_at": "2024-07-05T15:00:00Z",
  "is_active": true
}
```

### 3. List Sales Returns

Retrieve a list of sales returns with optional filtering and pagination.

**Endpoint**: `GET /sales/returns/`

**Query Parameters**:
- `sales_transaction_id` (UUID, optional): Filter by transaction
- `approved_by_id` (UUID, optional): Filter by approver
- `start_date` (ISO datetime, optional): Filter returns from this date
- `end_date` (ISO datetime, optional): Filter returns to this date
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 50): Maximum records to return
- `sort_by` (string, optional, default: "return_date"): Field to sort by
- `sort_desc` (boolean, optional, default: true): Sort in descending order

**Response** (`200 OK`):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "return_id": "RET-2024-001",
    "sales_transaction_id": "550e8400-e29b-41d4-a716-446655440010",
    "return_date": "2024-07-05T14:30:00Z",
    "reason": "Customer not satisfied with product quality",
    "refund_amount": "97.65",
    "restocking_fee": "9.77",
    "net_refund_amount": "87.88",
    "is_approved": true,
    "approved_by_name": "Manager Smith",
    "created_at": "2024-07-05T14:30:00Z"
  }
  // ... more returns
]
```

### 4. Update Sales Return

Update a sales return (only before approval).

**Endpoint**: `PATCH /sales/returns/{return_id}`

**Request Schema**:
```json
{
  "reason": "string (optional)",
  "restocking_fee": "decimal (optional)"
}
```

**Example Request**:
```json
{
  "reason": "Updated reason with additional details from customer",
  "restocking_fee": 15.0
}
```

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "return_id": "RET-2024-001",
  "reason": "Updated reason with additional details from customer",
  "restocking_fee": "14.65",
  "net_refund_amount": "83.00",
  // ... other fields
  "updated_at": "2024-07-05T15:30:00Z"
}
```

### 5. Approve Sales Return

Approve a sales return.

**Endpoint**: `POST /sales/returns/{return_id}/approve`

**Query Parameters**:
- `current_user_id` (UUID, required): ID of the user approving the return

**Request Schema**:
```json
{
  "notes": "string (optional)"
}
```

**Example Request**:
```json
{
  "notes": "Approved after inspection - item in good condition"
}
```

**Response** (`200 OK`):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440030",
  "return_id": "RET-2024-001",
  "is_approved": true,
  "approved_by_id": "550e8400-e29b-41d4-a716-446655440050",
  "reason": "Updated reason with additional details from customer\n\nApproval notes: Approved after inspection - item in good condition",
  // ... other fields
  "updated_at": "2024-07-05T16:00:00Z"
}
```

### 6. Get Return Summary

Get return summary statistics for a date range.

**Endpoint**: `GET /sales/returns/summary/stats`

**Query Parameters**:
- `start_date` (ISO datetime, required): Start date for summary
- `end_date` (ISO datetime, required): End date for summary

**Response** (`200 OK`):
```json
{
  "period": {
    "start_date": "2024-06-01T00:00:00Z",
    "end_date": "2024-06-30T23:59:59Z"
  },
  "total_returns": 15,
  "approved_count": 12,
  "pending_count": 3,
  "total_refund_amount": "2450.75",
  "approved_refund_amount": "2100.50",
  "pending_refund_amount": "350.25",
  "total_restocking_fees": "245.08",
  "average_refund_amount": "163.38"
}
```

### 7. Get Pending Approval Returns

Get all returns pending approval.

**Endpoint**: `GET /sales/returns/pending-approval`

**Response** (`200 OK`):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "return_id": "RET-2024-001",
    "sales_transaction_id": "550e8400-e29b-41d4-a716-446655440010",
    "return_date": "2024-07-05T14:30:00Z",
    "reason": "Customer not satisfied with product quality",
    "refund_amount": "97.65",
    "net_refund_amount": "87.88",
    "is_approved": false,
    "approved_by_id": null
  }
  // ... more pending returns
]
```

### 8. Get Returns by Transaction

Get all returns for a specific sales transaction.

**Endpoint**: `GET /sales/returns/by-transaction/{transaction_id}`

**Path Parameters**:
- `transaction_id` (UUID): The sales transaction ID

**Response** (`200 OK`):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440030",
    "return_id": "RET-2024-001",
    "sales_transaction_id": "550e8400-e29b-41d4-a716-446655440010",
    "return_date": "2024-07-05T14:30:00Z",
    "refund_amount": "97.65",
    "is_approved": true
  }
  // ... more returns for this transaction
]
```

---

## Common Schemas

### Sales Status Enum
```
DRAFT - Order is being created and can be modified
CONFIRMED - Order has been confirmed and stock is allocated
PROCESSING - Order is being prepared for shipment
SHIPPED - Order has been shipped to customer
DELIVERED - Order has been delivered to customer
CANCELLED - Order has been cancelled
```

### Payment Status Enum
```
PENDING - No payment has been received yet
PARTIAL - Partial payment has been received
PAID - Full payment has been received
OVERDUE - Payment is past the due date
REFUNDED - Payment has been refunded
```

### Payment Terms Enum
```
IMMEDIATE - Payment due immediately upon order
NET_15 - Payment due within 15 days
NET_30 - Payment due within 30 days
NET_45 - Payment due within 45 days
NET_60 - Payment due within 60 days
NET_90 - Payment due within 90 days
COD - Cash on delivery
PREPAID - Payment required before order processing
```

### Return Item Condition Enum
```
GOOD - Item in good condition, can be resold
DAMAGED - Item is damaged but may be repairable
DEFECTIVE - Item is defective and cannot be resold
OPENED - Item packaging has been opened
USED - Item shows signs of use
```

---

## Error Handling

All API endpoints return consistent error responses with appropriate HTTP status codes.

### Error Response Schema
```json
{
  "detail": "string", // Error message
  "error_code": "string (optional)", // Application-specific error code
  "validation_errors": {} // Field-specific validation errors (422 only)
}
```

### Common HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data or business logic violation
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server error

### Example Error Responses

**400 Bad Request**:
```json
{
  "detail": "Cannot update cancelled transaction"
}
```

**404 Not Found**:
```json
{
  "detail": "Sales transaction 550e8400-e29b-41d4-a716-446655440010 not found"
}
```

**422 Validation Error**:
```json
{
  "detail": "Validation failed",
  "validation_errors": {
    "customer_id": ["Field required"],
    "items": ["At least one item is required"]
  }
}
```

---

## Authentication

All API endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse:
- **Standard endpoints**: 100 requests per minute
- **Heavy operations** (create, update): 30 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1625097600
```

---

## Webhooks (Future)

The sales module will support webhooks for real-time updates:
- `sales.transaction.created`
- `sales.transaction.confirmed`
- `sales.transaction.paid`
- `sales.return.created`
- `sales.return.approved`

---

## SDK Examples

### JavaScript/TypeScript

```typescript
// Create a sales transaction
const transaction = await salesApi.createTransaction({
  customer_id: "550e8400-e29b-41d4-a716-446655440000",
  items: [{
    inventory_item_master_id: "550e8400-e29b-41d4-a716-446655440001",
    warehouse_id: "550e8400-e29b-41d4-a716-446655440002",
    quantity: 2,
    unit_price: "100.00",
    tax_rate: "8.5"
  }],
  payment_terms: "NET_30",
  shipping_amount: "25.00"
});

// Process payment
await salesApi.processPayment(transaction.id, {
  payment_amount: transaction.grand_total,
  payment_method: "CREDIT_CARD",
  reference_number: "CC-12345678"
});

// Create return
const salesReturn = await salesApi.createReturn({
  sales_transaction_id: transaction.id,
  reason: "Customer changed mind",
  items: [{
    sales_item_id: transaction.items[0].id,
    quantity: 1,
    condition: "GOOD"
  }],
  restocking_fee: 10.0
});
```

This documentation provides comprehensive coverage of the Sales Module API, including detailed request/response examples, error handling, and practical usage information for frontend developers.