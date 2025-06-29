# Inventory Item Master API Documentation

## Overview

The Inventory Item Master module manages the master catalog of all inventory items in the rental management system. It supports both bulk and individual item tracking, with comprehensive metadata and dimensional information.

## Base URL

```
/api/v1/inventory-items
```

## Authentication

All endpoints require valid authentication (implementation dependent on auth system).

---

## 📋 Table of Contents

1. [Create Item Master](#1-create-item-master)
2. [Get Item Master by ID](#2-get-item-master-by-id)
3. [Get Item Master by SKU](#3-get-item-master-by-sku)
4. [Update Item Master](#4-update-item-master)
5. [Delete Item Master](#5-delete-item-master)
6. [List Item Masters](#6-list-item-masters)
7. [List by Subcategory](#7-list-by-subcategory)
8. [List by Tracking Type](#8-list-by-tracking-type)
9. [List Consumable Items](#9-list-consumable-items)
10. [Search Items](#10-search-items)
11. [Update Quantity](#11-update-quantity)
12. [Update Dimensions](#12-update-dimensions)
13. [Data Models](#data-models)
14. [Error Responses](#error-responses)

---

## 1. Create Item Master

Creates a new inventory item master record.

### Endpoint
```http
POST /api/v1/inventory-items/
```

### Request Payload

```json
{
  "name": "string (required, 1-255 chars, unique)",
  "sku": "string (required, 1-255 chars, unique, auto-uppercase)",
  "description": "string (optional)",
  "contents": "string (optional)",
  "item_sub_category_id": "uuid (required)",
  "unit_of_measurement_id": "uuid (required)",
  "packaging_id": "uuid (optional)",
  "tracking_type": "string (required, BULK or INDIVIDUAL)",
  "is_consumable": "boolean (optional, default: false)",
  "brand": "string (optional, max 255 chars)",
  "manufacturer_part_number": "string (optional, max 255 chars)",
  "product_id": "string (optional, max 255 chars)",
  "weight": "decimal (optional, >= 0, in kilograms)",
  "length": "decimal (optional, >= 0, in centimeters)",
  "width": "decimal (optional, >= 0, in centimeters)",
  "height": "decimal (optional, >= 0, in centimeters)",
  "renting_period": "integer (optional, default: 1, >= 1, in days)",
  "quantity": "integer (optional, default: 0, >= 0)",
  "created_by": "string (optional)"
}
```

### Example Request

```json
{
  "name": "MacBook Pro 16-inch",
  "sku": "MBP16-001",
  "description": "Apple MacBook Pro with M2 chip, 16GB RAM, 512GB SSD",
  "contents": "Laptop, Charger, Documentation",
  "item_sub_category_id": "550e8400-e29b-41d4-a716-446655440000",
  "unit_of_measurement_id": "660f8500-e29b-41d4-a716-446655440001",
  "packaging_id": "770a8600-e29b-41d4-a716-446655440002",
  "tracking_type": "INDIVIDUAL",
  "is_consumable": false,
  "brand": "Apple",
  "manufacturer_part_number": "MBP16-M2-16-512",
  "product_id": "APPLE-MBP-2023-001",
  "weight": 2.15,
  "length": 35.57,
  "width": 24.81,
  "height": 1.68,
  "renting_period": 7,
  "quantity": 5,
  "created_by": "admin@company.com"
}
```

### Response (201 Created)

```json
{
  "id": "880b8700-e29b-41d4-a716-446655440003",
  "name": "MacBook Pro 16-inch",
  "sku": "MBP16-001",
  "description": "Apple MacBook Pro with M2 chip, 16GB RAM, 512GB SSD",
  "contents": "Laptop, Charger, Documentation",
  "item_sub_category_id": "550e8400-e29b-41d4-a716-446655440000",
  "unit_of_measurement_id": "660f8500-e29b-41d4-a716-446655440001",
  "packaging_id": "770a8600-e29b-41d4-a716-446655440002",
  "tracking_type": "INDIVIDUAL",
  "is_consumable": false,
  "brand": "Apple",
  "manufacturer_part_number": "MBP16-M2-16-512",
  "product_id": "APPLE-MBP-2023-001",
  "weight": 2.15,
  "length": 35.57,
  "width": 24.81,
  "height": 1.68,
  "renting_period": 7,
  "quantity": 5,
  "created_at": "2023-12-01T10:30:00Z",
  "updated_at": "2023-12-01T10:30:00Z",
  "created_by": "admin@company.com",
  "is_active": true
}
```

---

## 2. Get Item Master by ID

Retrieves a specific inventory item master by its unique ID.

### Endpoint
```http
GET /api/v1/inventory-items/{item_id}
```

### Path Parameters
- `item_id` (UUID, required): The unique identifier of the inventory item

### Example Request
```http
GET /api/v1/inventory-items/880b8700-e29b-41d4-a716-446655440003
```

### Response (200 OK)
```json
{
  "id": "880b8700-e29b-41d4-a716-446655440003",
  "name": "MacBook Pro 16-inch",
  "sku": "MBP16-001",
  "description": "Apple MacBook Pro with M2 chip, 16GB RAM, 512GB SSD",
  "contents": "Laptop, Charger, Documentation",
  "item_sub_category_id": "550e8400-e29b-41d4-a716-446655440000",
  "unit_of_measurement_id": "660f8500-e29b-41d4-a716-446655440001",
  "packaging_id": "770a8600-e29b-41d4-a716-446655440002",
  "tracking_type": "INDIVIDUAL",
  "is_consumable": false,
  "brand": "Apple",
  "manufacturer_part_number": "MBP16-M2-16-512",
  "product_id": "APPLE-MBP-2023-001",
  "weight": 2.15,
  "length": 35.57,
  "width": 24.81,
  "height": 1.68,
  "renting_period": 7,
  "quantity": 5,
  "created_at": "2023-12-01T10:30:00Z",
  "updated_at": "2023-12-01T10:30:00Z",
  "created_by": "admin@company.com",
  "is_active": true
}
```

---

## 3. Get Item Master by SKU

Retrieves a specific inventory item master by its SKU.

### Endpoint
```http
GET /api/v1/inventory-items/by-sku/{sku}
```

### Path Parameters
- `sku` (string, required): The Stock Keeping Unit of the inventory item

### Example Request
```http
GET /api/v1/inventory-items/by-sku/MBP16-001
```

### Response (200 OK)
Same as [Get Item Master by ID](#2-get-item-master-by-id) response.

---

## 4. Update Item Master

Updates an existing inventory item master. All fields are optional in the update payload.

### Endpoint
```http
PUT /api/v1/inventory-items/{item_id}
```

### Path Parameters
- `item_id` (UUID, required): The unique identifier of the inventory item

### Request Payload

```json
{
  "name": "string (optional, 1-255 chars, unique)",
  "sku": "string (optional, 1-255 chars, unique, auto-uppercase)",
  "description": "string (optional)",
  "contents": "string (optional)",
  "item_sub_category_id": "uuid (optional)",
  "unit_of_measurement_id": "uuid (optional)",
  "packaging_id": "uuid (optional)",
  "tracking_type": "string (optional, BULK or INDIVIDUAL)",
  "is_consumable": "boolean (optional)",
  "brand": "string (optional, max 255 chars)",
  "manufacturer_part_number": "string (optional, max 255 chars)",
  "product_id": "string (optional, max 255 chars)",
  "weight": "decimal (optional, >= 0, in kilograms)",
  "length": "decimal (optional, >= 0, in centimeters)",
  "width": "decimal (optional, >= 0, in centimeters)",
  "height": "decimal (optional, >= 0, in centimeters)",
  "renting_period": "integer (optional, >= 1, in days)",
  "quantity": "integer (optional, >= 0)",
  "is_active": "boolean (optional)"
}
```

### Example Request

```json
{
  "name": "MacBook Pro 16-inch (Updated)",
  "description": "Apple MacBook Pro with M2 Pro chip, 32GB RAM, 1TB SSD",
  "weight": 2.2,
  "quantity": 8,
  "renting_period": 14
}
```

### Response (200 OK)
Returns the updated item master object with all fields populated.

---

## 5. Delete Item Master

Soft deletes an inventory item master (sets is_active to false).

### Endpoint
```http
DELETE /api/v1/inventory-items/{item_id}
```

### Path Parameters
- `item_id` (UUID, required): The unique identifier of the inventory item

### Example Request
```http
DELETE /api/v1/inventory-items/880b8700-e29b-41d4-a716-446655440003
```

### Response (204 No Content)
No response body. HTTP status 204 indicates successful deletion.

---

## 6. List Item Masters

Retrieves a paginated list of inventory item masters.

### Endpoint
```http
GET /api/v1/inventory-items/
```

### Query Parameters
- `skip` (integer, optional, default: 0, >= 0): Number of records to skip for pagination
- `limit` (integer, optional, default: 100, 1-1000): Maximum number of records to return

### Example Request
```http
GET /api/v1/inventory-items/?skip=0&limit=20
```

### Response (200 OK)

```json
{
  "items": [
    {
      "id": "880b8700-e29b-41d4-a716-446655440003",
      "name": "MacBook Pro 16-inch",
      "sku": "MBP16-001",
      "description": "Apple MacBook Pro with M2 chip",
      "contents": "Laptop, Charger, Documentation",
      "item_sub_category_id": "550e8400-e29b-41d4-a716-446655440000",
      "unit_of_measurement_id": "660f8500-e29b-41d4-a716-446655440001",
      "packaging_id": "770a8600-e29b-41d4-a716-446655440002",
      "tracking_type": "INDIVIDUAL",
      "is_consumable": false,
      "brand": "Apple",
      "manufacturer_part_number": "MBP16-M2-16-512",
      "product_id": "APPLE-MBP-2023-001",
      "weight": 2.15,
      "length": 35.57,
      "width": 24.81,
      "height": 1.68,
      "renting_period": 7,
      "quantity": 5,
      "created_at": "2023-12-01T10:30:00Z",
      "updated_at": "2023-12-01T10:30:00Z",
      "created_by": "admin@company.com",
      "is_active": true
    },
    {
      "id": "990c8800-e29b-41d4-a716-446655440004",
      "name": "Steel Screws M6x20",
      "sku": "SCREW-M6-20",
      "description": "Stainless steel screws M6x20mm",
      "contents": null,
      "item_sub_category_id": "551e8401-e29b-41d4-a716-446655440001",
      "unit_of_measurement_id": "661f8501-e29b-41d4-a716-446655440002",
      "packaging_id": null,
      "tracking_type": "BULK",
      "is_consumable": false,
      "brand": "FastenerPro",
      "manufacturer_part_number": "FP-M6-20-SS",
      "product_id": null,
      "weight": 0.005,
      "length": 2.0,
      "width": 0.6,
      "height": 0.6,
      "renting_period": 1,
      "quantity": 500,
      "created_at": "2023-12-01T11:15:00Z",
      "updated_at": "2023-12-01T11:15:00Z",
      "created_by": "admin@company.com",
      "is_active": true
    }
  ],
  "total": 142,
  "skip": 0,
  "limit": 20
}
```

---

## 7. List by Subcategory

Retrieves inventory items filtered by subcategory.

### Endpoint
```http
GET /api/v1/inventory-items/by-subcategory/{subcategory_id}
```

### Path Parameters
- `subcategory_id` (UUID, required): The subcategory identifier

### Query Parameters
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 100): Maximum number of records to return

### Example Request
```http
GET /api/v1/inventory-items/by-subcategory/550e8400-e29b-41d4-a716-446655440000?skip=0&limit=10
```

### Response (200 OK)
Returns an array of inventory item objects belonging to the specified subcategory.

---

## 8. List by Tracking Type

Retrieves inventory items filtered by tracking type.

### Endpoint
```http
GET /api/v1/inventory-items/by-tracking-type/{tracking_type}
```

### Path Parameters
- `tracking_type` (string, required): Either "BULK" or "INDIVIDUAL"

### Query Parameters
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 100): Maximum number of records to return

### Example Request
```http
GET /api/v1/inventory-items/by-tracking-type/INDIVIDUAL?skip=0&limit=10
```

### Response (200 OK)
Returns an array of inventory item objects with the specified tracking type.

---

## 9. List Consumable Items

Retrieves all consumable inventory items.

### Endpoint
```http
GET /api/v1/inventory-items/consumables/
```

### Query Parameters
- `skip` (integer, optional, default: 0): Number of records to skip
- `limit` (integer, optional, default: 100): Maximum number of records to return

### Example Request
```http
GET /api/v1/inventory-items/consumables/?skip=0&limit=10
```

### Response (200 OK)
Returns an array of consumable inventory item objects (where `is_consumable` is true).

---

## 10. Search Items

Searches inventory items across multiple fields.

### Endpoint
```http
GET /api/v1/inventory-items/search/
```

### Query Parameters
- `query` (string, required, min length: 1): Search query string
- `search_fields` (array of strings, optional): Fields to search in. Default: ["name", "sku", "description", "brand", "manufacturer_part_number"]
- `limit` (integer, optional, default: 10, 1-100): Maximum number of results

### Example Request
```http
GET /api/v1/inventory-items/search/?query=MacBook&limit=5
```

### Advanced Search Request
```http
GET /api/v1/inventory-items/search/?query=Apple&search_fields=name&search_fields=brand&limit=10
```

### Response (200 OK)
Returns an array of inventory item objects matching the search criteria.

---

## 11. Update Quantity

Updates only the quantity of an inventory item.

### Endpoint
```http
PATCH /api/v1/inventory-items/{item_id}/quantity
```

### Path Parameters
- `item_id` (UUID, required): The unique identifier of the inventory item

### Request Payload

```json
{
  "quantity": "integer (required, >= 0)"
}
```

### Example Request

```json
{
  "quantity": 50
}
```

### Response (200 OK)

```json
{
  "message": "Quantity updated successfully",
  "new_quantity": 50
}
```

---

## 12. Update Dimensions

Updates only the physical dimensions of an inventory item.

### Endpoint
```http
PATCH /api/v1/inventory-items/{item_id}/dimensions
```

### Path Parameters
- `item_id` (UUID, required): The unique identifier of the inventory item

### Request Payload

```json
{
  "weight": "decimal (optional, >= 0, in kilograms)",
  "length": "decimal (optional, >= 0, in centimeters)",
  "width": "decimal (optional, >= 0, in centimeters)",
  "height": "decimal (optional, >= 0, in centimeters)"
}
```

### Example Request

```json
{
  "weight": 2.5,
  "length": 36.0,
  "width": 25.0,
  "height": 1.8
}
```

### Response (200 OK)
Returns the updated item master object with new dimensions.

---

## Data Models

### Tracking Types
- **BULK**: Items tracked as quantities (e.g., screws, paper sheets)
- **INDIVIDUAL**: Items tracked individually with unique identifiers (e.g., laptops, tools)

### Field Validations

#### Required Fields (Create)
- `name`: Unique, 1-255 characters
- `sku`: Unique, 1-255 characters, auto-converted to uppercase
- `item_sub_category_id`: Valid UUID of existing subcategory
- `unit_of_measurement_id`: Valid UUID of existing unit
- `tracking_type`: Must be "BULK" or "INDIVIDUAL"

#### Optional Fields
- `description`: Free text description
- `contents`: Item contents or composition
- `packaging_id`: UUID of packaging type
- `is_consumable`: Boolean (default: false)
- `brand`: Brand name (max 255 chars)
- `manufacturer_part_number`: Manufacturer's part number (max 255 chars)
- `product_id`: Additional product identifier (max 255 chars)
- `weight`: Decimal in kilograms (>= 0)
- `length`: Decimal in centimeters (>= 0)
- `width`: Decimal in centimeters (>= 0)
- `height`: Decimal in centimeters (>= 0)
- `renting_period`: Integer in days (>= 1, default: 1)
- `quantity`: Integer (>= 0, default: 0)

#### Auto-Generated Fields
- `id`: UUID primary key
- `created_at`: Timestamp
- `updated_at`: Timestamp (updated on modifications)
- `is_active`: Boolean (default: true)

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "An item with SKU 'MBP16-001' already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Inventory item not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "tracking_type"],
      "msg": "Tracking type must be either BULK or INDIVIDUAL",
      "type": "value_error"
    }
  ]
}
```

### Common Error Scenarios

1. **Duplicate SKU/Name**: Returns 400 with descriptive message
2. **Invalid tracking type**: Returns 422 with validation details
3. **Negative dimensions**: Returns 422 with validation details
4. **Invalid UUID format**: Returns 422 with validation details
5. **Missing required fields**: Returns 422 with field details
6. **Item not found**: Returns 404 for GET, PUT, DELETE operations

---

## Usage Examples

### Creating a Bulk Item (Consumable)
```json
{
  "name": "A4 Paper Sheets",
  "sku": "PAPER-A4-001",
  "description": "High quality A4 paper for printing",
  "item_sub_category_id": "aa1e8400-e29b-41d4-a716-446655440000",
  "unit_of_measurement_id": "bb1f8500-e29b-41d4-a716-446655440001",
  "tracking_type": "BULK",
  "is_consumable": true,
  "brand": "OfficeMax",
  "quantity": 1000,
  "renting_period": 1
}
```

### Creating an Individual Item (Equipment)
```json
{
  "name": "Professional Camera",
  "sku": "CAM-PRO-001",
  "description": "Canon EOS R5 with 24-70mm lens",
  "item_sub_category_id": "cc2e8400-e29b-41d4-a716-446655440000",
  "unit_of_measurement_id": "dd2f8500-e29b-41d4-a716-446655440001",
  "tracking_type": "INDIVIDUAL",
  "is_consumable": false,
  "brand": "Canon",
  "manufacturer_part_number": "EOS-R5-2470",
  "weight": 1.2,
  "renting_period": 3,
  "quantity": 2
}
```

### Partial Update Example
```json
{
  "quantity": 15,
  "renting_period": 10,
  "description": "Updated description with new specifications"
}
```

This documentation provides comprehensive guidance for integrating with the Inventory Item Master API, including all required payloads, response formats, and common usage patterns.