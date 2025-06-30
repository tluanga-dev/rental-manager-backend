# Purchase Transaction API Documentation

## Overview

The Purchase Transaction API provides comprehensive functionality for managing purchase transactions from vendors. This includes creating transactions, managing transaction items, tracking status workflows, and generating reports.

**Base URL**: `http://localhost:8000/api/v1/purchase-transactions`

## Table of Contents

1. [Authentication](#authentication)
2. [Transaction Management](#transaction-management)
3. [Transaction Items](#transaction-items)
4. [Search & Filtering](#search--filtering)
5. [Statistics & Reporting](#statistics--reporting)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Authentication

All API endpoints require authentication via Bearer token:

```http
Authorization: Bearer <your-jwt-token>
```

## Transaction Management

### Create Transaction

Create a new purchase transaction.

**Endpoint**: `POST /api/v1/purchase-transactions/`

**Request Body**:
```json
{
  "transaction_date": "2024-01-15",
  "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
  "purchase_order_number": "PO-2024-001",
  "remarks": "Monthly inventory purchase",
  "created_by": "user123"
}
```

**Response** (201 Created):
```json
{
  "transaction": {
    "id": "987f6543-a21b-34c5-d678-987654321000",
    "transaction_id": "PUR-2024-001",
    "transaction_date": "2024-01-15",
    "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "DRAFT",
    "total_amount": "0.00",
    "grand_total": "0.00",
    "purchase_order_number": "PO-2024-001",
    "remarks": "Monthly inventory purchase",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "created_by": "user123",
    "is_active": true
  },
  "message": "Purchase transaction created successfully"
}
```

### Create Transaction with Items

Create a transaction and its items atomically.

**Endpoint**: `POST /api/v1/purchase-transactions/with-items/`

**Request Body**:
```json
{
  "transaction_date": "2024-01-15",
  "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
  "purchase_order_number": "PO-2024-002",
  "remarks": "Bulk purchase with items",
  "created_by": "user123",
  "items": [
    {
      "item_master_id": "item-001",
      "quantity": 10,
      "unit_price": "25.50",
      "warehouse_id": "warehouse-001",
      "discount": "5.00",
      "tax_amount": "3.50",
      "warranty_period_type": "MONTHS",
      "warranty_period": 12
    },
    {
      "item_master_id": "item-002",
      "quantity": 5,
      "unit_price": "150.00",
      "warehouse_id": "warehouse-001",
      "serial_number": ["SN001", "SN002", "SN003", "SN004", "SN005"]
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "transaction": {
    "id": "987f6543-a21b-34c5-d678-987654321001",
    "transaction_id": "PUR-2024-002",
    "transaction_date": "2024-01-15",
    "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
    "status": "DRAFT",
    "total_amount": "1003.50",
    "grand_total": "1003.50",
    "purchase_order_number": "PO-2024-002",
    "remarks": "Bulk purchase with items",
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z",
    "created_by": "user123",
    "is_active": true
  },
  "message": "Purchase transaction with items created successfully"
}
```

### Get Transaction List

Retrieve a paginated list of transactions with optional filtering.

**Endpoint**: `GET /api/v1/purchase-transactions/`

**Query Parameters**:
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50): Items per page
- `vendor_id` (UUID, optional): Filter by vendor
- `status` (string, optional): Filter by status
- `date_from` (date, optional): Start date filter (YYYY-MM-DD)
- `date_to` (date, optional): End date filter (YYYY-MM-DD)
- `purchase_order_number` (string, optional): Filter by PO number
- `sort_by` (string, optional): Sort field
- `sort_desc` (boolean, default: true): Sort direction

**Example Request**:
```http
GET /api/v1/purchase-transactions/?page=1&page_size=10&status=CONFIRMED&vendor_id=123e4567-e89b-12d3-a456-426614174000
```

**Response** (200 OK):
```json
{
  "transactions": [
    {
      "id": "987f6543-a21b-34c5-d678-987654321000",
      "transaction_id": "PUR-2024-001",
      "transaction_date": "2024-01-15",
      "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "CONFIRMED",
      "total_amount": "500.00",
      "grand_total": "500.00",
      "purchase_order_number": "PO-2024-001",
      "remarks": "Monthly inventory purchase",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T12:00:00Z",
      "created_by": "user123",
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

### Get Transaction Details

Get a specific transaction with its items.

**Endpoint**: `GET /api/v1/purchase-transactions/{transaction_id}/`

**Response** (200 OK):
```json
{
  "id": "987f6543-a21b-34c5-d678-987654321000",
  "transaction_id": "PUR-2024-001",
  "transaction_date": "2024-01-15",
  "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "CONFIRMED",
  "total_amount": "500.00",
  "grand_total": "500.00",
  "purchase_order_number": "PO-2024-001",
  "remarks": "Monthly inventory purchase",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "created_by": "user123",
  "is_active": true,
  "items": [
    {
      "id": "item-id-001",
      "transaction_id": "987f6543-a21b-34c5-d678-987654321000",
      "inventory_item_id": "item-001",
      "warehouse_id": "warehouse-001",
      "quantity": 10,
      "unit_price": "25.50",
      "discount": "5.00",
      "tax_amount": "3.50",
      "total_price": "254.00",
      "serial_number": [],
      "remarks": null,
      "warranty_period_type": "MONTHS",
      "warranty_period": 12,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "created_by": "user123",
      "is_active": true
    }
  ],
  "item_summary": {
    "total_items": 1,
    "total_quantity": 10,
    "total_amount": "254.00",
    "total_discount": "5.00",
    "total_tax": "3.50",
    "average_unit_price": "25.50",
    "items_with_warranty": 1,
    "items_with_serial_numbers": 0
  }
}
```

### Get Transaction by Transaction ID

Get a transaction using its transaction ID string.

**Endpoint**: `GET /api/v1/purchase-transactions/by-transaction-id/{transaction_id}/`

**Example**: `GET /api/v1/purchase-transactions/by-transaction-id/PUR-2024-001/`

### Update Transaction

Update transaction details.

**Endpoint**: `PUT /api/v1/purchase-transactions/{transaction_id}/`

**Request Body**:
```json
{
  "vendor_id": "123e4567-e89b-12d3-a456-426614174001",
  "transaction_date": "2024-01-16",
  "purchase_order_number": "PO-2024-001-UPDATED",
  "remarks": "Updated remarks"
}
```

**Response** (200 OK):
```json
{
  "transaction": {
    "id": "987f6543-a21b-34c5-d678-987654321000",
    "transaction_id": "PUR-2024-001",
    "transaction_date": "2024-01-16",
    "vendor_id": "123e4567-e89b-12d3-a456-426614174001",
    "status": "DRAFT",
    "total_amount": "500.00",
    "grand_total": "500.00",
    "purchase_order_number": "PO-2024-001-UPDATED",
    "remarks": "Updated remarks",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T09:15:00Z",
    "created_by": "user123",
    "is_active": true
  },
  "message": "Purchase transaction updated successfully"
}
```

### Update Transaction Status

Update only the transaction status.

**Endpoint**: `PATCH /api/v1/purchase-transactions/{transaction_id}/status/`

**Request Body**:
```json
{
  "status": "CONFIRMED"
}
```

**Valid Status Values**:
- `DRAFT` - Initial state
- `CONFIRMED` - Transaction confirmed
- `PROCESSING` - Being processed
- `RECEIVED` - Items received
- `COMPLETED` - Transaction completed
- `CANCELLED` - Transaction cancelled

**Response** (200 OK):
```json
{
  "transaction": {
    "id": "987f6543-a21b-34c5-d678-987654321000",
    "transaction_id": "PUR-2024-001",
    "status": "CONFIRMED",
    // ... other fields
  },
  "message": "Purchase transaction status updated to CONFIRMED"
}
```

### Delete Transaction

Soft delete a transaction (sets is_active to false).

**Endpoint**: `DELETE /api/v1/purchase-transactions/{transaction_id}/`

**Response** (200 OK):
```json
{
  "message": "Purchase transaction deleted successfully",
  "transaction_id": "987f6543-a21b-34c5-d678-987654321000"
}
```

## Transaction Items

### Get Transaction Items

Get items for a specific transaction with pagination.

**Endpoint**: `GET /api/v1/purchase-transactions/{transaction_id}/items/`

**Query Parameters**:
- `page` (integer, default: 1): Page number
- `page_size` (integer, default: 50): Items per page

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "item-id-001",
      "transaction_id": "987f6543-a21b-34c5-d678-987654321000",
      "inventory_item_id": "item-001",
      "warehouse_id": "warehouse-001",
      "quantity": 10,
      "unit_price": "25.50",
      "discount": "5.00",
      "tax_amount": "3.50",
      "total_price": "254.00",
      "serial_number": [],
      "remarks": null,
      "warranty_period_type": "MONTHS",
      "warranty_period": 12,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "created_by": "user123",
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50,
  "total_pages": 1
}
```

### Add Transaction Item

Add a single item to a transaction.

**Endpoint**: `POST /api/v1/purchase-transactions/{transaction_id}/items/`

**Request Body**:
```json
{
  "item_master_id": "item-003",
  "quantity": 5,
  "unit_price": "75.00",
  "warehouse_id": "warehouse-001",
  "serial_number": ["SN101", "SN102", "SN103", "SN104", "SN105"],
  "discount": "10.00",
  "tax_amount": "5.50",
  "remarks": "Special order item",
  "warranty_period_type": "YEARS",
  "warranty_period": 2
}
```

**Response** (200 OK):
```json
{
  "item": {
    "id": "item-id-002",
    "transaction_id": "987f6543-a21b-34c5-d678-987654321000",
    "inventory_item_id": "item-003",
    "warehouse_id": "warehouse-001",
    "quantity": 5,
    "unit_price": "75.00",
    "discount": "10.00",
    "tax_amount": "5.50",
    "total_price": "370.50",
    "serial_number": ["SN101", "SN102", "SN103", "SN104", "SN105"],
    "remarks": "Special order item",
    "warranty_period_type": "YEARS",
    "warranty_period": 2,
    "created_at": "2024-01-15T14:00:00Z",
    "updated_at": "2024-01-15T14:00:00Z",
    "created_by": "user123",
    "is_active": true
  },
  "message": "Transaction item created successfully"
}
```

### Bulk Add Items

Add multiple items to a transaction atomically.

**Endpoint**: `POST /api/v1/purchase-transactions/{transaction_id}/items/bulk/`

**Request Body**:
```json
{
  "items": [
    {
      "item_master_id": "item-004",
      "quantity": 3,
      "unit_price": "120.00"
    },
    {
      "item_master_id": "item-005",
      "quantity": 2,
      "unit_price": "200.00",
      "warranty_period_type": "MONTHS",
      "warranty_period": 6
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "created_items": [
    {
      "id": "item-id-003",
      "transaction_id": "987f6543-a21b-34c5-d678-987654321000",
      "inventory_item_id": "item-004",
      "quantity": 3,
      "unit_price": "120.00",
      "total_price": "360.00",
      // ... other fields
    },
    {
      "id": "item-id-004",
      "transaction_id": "987f6543-a21b-34c5-d678-987654321000",
      "inventory_item_id": "item-005",
      "quantity": 2,
      "unit_price": "200.00",
      "total_price": "400.00",
      // ... other fields
    }
  ],
  "total_created": 2,
  "total_requested": 2,
  "transaction_id": "987f6543-a21b-34c5-d678-987654321000",
  "updated_totals": {
    "total_amount": "1130.50",
    "grand_total": "1130.50"
  }
}
```

### Get Transaction Item

Get a specific item within a transaction.

**Endpoint**: `GET /api/v1/purchase-transactions/{transaction_id}/items/{item_id}/`

### Update Transaction Item

Update an existing transaction item.

**Endpoint**: `PUT /api/v1/purchase-transactions/{transaction_id}/items/{item_id}/`

**Request Body**:
```json
{
  "unit_price": "80.00",
  "discount": "15.00",
  "tax_amount": "6.00",
  "remarks": "Updated pricing",
  "warranty_period_type": "MONTHS",
  "warranty_period": 18
}
```

### Delete Transaction Item

Remove an item from a transaction.

**Endpoint**: `DELETE /api/v1/purchase-transactions/{transaction_id}/items/{item_id}/`

**Response** (200 OK):
```json
{
  "message": "Transaction item deleted successfully",
  "item_id": "item-id-001"
}
```

## Search & Filtering

### Search Transactions

Search transactions using text query.

**Endpoint**: `POST /api/v1/purchase-transactions/search/`

**Request Body**:
```json
{
  "query": "PO-2024",
  "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "CONFIRMED",
  "limit": 20
}
```

**Response** (200 OK):
```json
{
  "transactions": [
    {
      "id": "987f6543-a21b-34c5-d678-987654321000",
      "transaction_id": "PUR-2024-001",
      "transaction_date": "2024-01-15",
      "vendor_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "CONFIRMED",
      "total_amount": "500.00",
      "grand_total": "500.00",
      "purchase_order_number": "PO-2024-001",
      "remarks": "Monthly inventory purchase",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T12:00:00Z",
      "created_by": "user123",
      "is_active": true
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 1,
  "total_pages": 1
}
```

## Statistics & Reporting

### Get Transaction Summary

Get summary statistics for a specific transaction.

**Endpoint**: `GET /api/v1/purchase-transactions/{transaction_id}/summary/`

**Response** (200 OK):
```json
{
  "total_items": 3,
  "total_quantity": 18,
  "total_amount": "1130.50",
  "total_discount": "30.00",
  "total_tax": "15.00",
  "average_unit_price": "75.25",
  "items_with_warranty": 2,
  "items_with_serial_numbers": 1
}
```

### Get Overall Statistics

Get overall purchase transaction statistics.

**Endpoint**: `GET /api/v1/purchase-transactions/statistics/summary/`

**Response** (200 OK):
```json
{
  "total_amount": "125000.00",
  "total_transactions": 45,
  "recent_amount": "15000.00",
  "recent_transactions": 8,
  "status_counts": {
    "DRAFT": 5,
    "CONFIRMED": 12,
    "PROCESSING": 8,
    "RECEIVED": 15,
    "COMPLETED": 4,
    "CANCELLED": 1
  }
}
```

## Data Models

### Transaction Status Workflow

```
DRAFT → CONFIRMED → PROCESSING → RECEIVED → COMPLETED
  ↓         ↓           ↓           ↓
CANCELLED ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←
```

### Warranty Period Types

- `DAYS` - Warranty period in days
- `MONTHS` - Warranty period in months  
- `YEARS` - Warranty period in years

### Required Fields

**Transaction Creation**:
- `transaction_date` (date)
- `vendor_id` (UUID)
- `created_by` (string)

**Transaction Item Creation**:
- `item_master_id` (UUID)
- `quantity` (integer > 0)
- `unit_price` (decimal ≥ 0)

### Validation Rules

1. **Transaction Date**: Cannot be in the future
2. **Serial Numbers**: For individually tracked items, number of serial numbers must equal quantity
3. **Warranty**: If warranty_period_type is provided, warranty_period must also be provided
4. **Amounts**: All price fields must be non-negative
5. **Status Transitions**: Must follow the defined workflow

## Error Handling

### HTTP Status Codes

- `200 OK` - Successful operation
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "detail": "Validation error message",
  "type": "validation_error",
  "errors": [
    {
      "field": "transaction_date",
      "message": "Transaction date cannot be in the future"
    }
  ]
}
```

## Examples

### Complete Transaction Workflow

1. **Create Transaction**:
```javascript
const transaction = await fetch('/api/v1/purchase-transactions/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    transaction_date: '2024-01-15',
    vendor_id: 'vendor-uuid',
    purchase_order_number: 'PO-2024-001',
    created_by: 'user123'
  })
});
```

2. **Add Items**:
```javascript
const item = await fetch(`/api/v1/purchase-transactions/${transactionId}/items/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    item_master_id: 'item-uuid',
    quantity: 10,
    unit_price: '25.50',
    warehouse_id: 'warehouse-uuid'
  })
});
```

3. **Confirm Transaction**:
```javascript
const confirmed = await fetch(`/api/v1/purchase-transactions/${transactionId}/status/`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    status: 'CONFIRMED'
  })
});
```

### Search with Filters

```javascript
const searchResults = await fetch('/api/v1/purchase-transactions/?' + new URLSearchParams({
  page: 1,
  page_size: 20,
  vendor_id: 'vendor-uuid',
  status: 'CONFIRMED',
  date_from: '2024-01-01',
  date_to: '2024-01-31',
  sort_by: 'transaction_date',
  sort_desc: true
}), {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

### Bulk Item Creation

```javascript
const bulkItems = await fetch(`/api/v1/purchase-transactions/${transactionId}/items/bulk/`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    items: [
      {
        item_master_id: 'item1-uuid',
        quantity: 5,
        unit_price: '100.00',
        warranty_period_type: 'MONTHS',
        warranty_period: 12
      },
      {
        item_master_id: 'item2-uuid',
        quantity: 3,
        unit_price: '200.00'
      }
    ]
  })
});
```

## Integration Notes

1. **Authentication**: All endpoints require valid JWT token
2. **CORS**: API supports cross-origin requests from frontend domain
3. **Rate Limiting**: Standard rate limits apply (contact admin for specifics)
4. **Pagination**: Use `page` and `page_size` parameters for large datasets
5. **Caching**: GET endpoints support ETags for caching
6. **Real-time**: Consider WebSocket connection for real-time updates
7. **File Uploads**: Not currently supported (planned for future releases)

## Support

For technical support or questions about this API:
- **Documentation**: This document
- **API Testing**: Use the interactive docs at `/docs` when server is running
- **Issue Reporting**: Contact the backend development team

---

*Last Updated: January 2024*
*API Version: v1*