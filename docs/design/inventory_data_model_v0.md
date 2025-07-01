# Comprehensive Inventory Management System - Data Model Design

## Table of Contents
1. [Core Master Tables](#core-master-tables)
2. [User & Access Management](#user--access-management)
3. [Customer Management](#customer-management)
4. [Product & SKU Management](#product--sku-management)
5. [Inventory Management](#inventory-management)
6. [Transaction Management](#transaction-management)
7. [Pricing & Discount Management](#pricing--discount-management)
8. [Payment & Financial Management](#payment--financial-management)
9. [Rental-Specific Tables](#rental-specific-tables)
10. [Sales-Specific Tables](#sales-specific-tables)
11. [Document Management](#document-management)
12. [Inspection & Quality Control](#inspection--quality-control)
13. [Analytics & Reporting](#analytics--reporting)
14. [System Configuration](#system-configuration)
15. [Entity Relationship Summary](#entity-relationship-summary)

---

## Core Master Tables

### LOCATION
**Description**: Physical locations including stores, warehouses, and service centers
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| location_id | INT | PK, AUTO_INCREMENT | Unique location identifier |
| location_code | VARCHAR(20) | UNIQUE, NOT NULL | Business location code |
| location_name | VARCHAR(100) | NOT NULL | Location display name |
| location_type | ENUM | NOT NULL | STORE, WAREHOUSE, SERVICE_CENTER |
| address | TEXT | NOT NULL | Full address |
| city | VARCHAR(50) | NOT NULL | City name |
| state | VARCHAR(50) | NOT NULL | State/Province |
| country | VARCHAR(50) | NOT NULL | Country |
| postal_code | VARCHAR(20) | | ZIP/Postal code |
| contact_number | VARCHAR(20) | | Primary phone |
| email | VARCHAR(100) | | Location email |
| manager_user_id | INT | FK → USER | Location manager |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_date | DATETIME | NOT NULL | Creation timestamp |
| modified_date | DATETIME | | Last modification |

---

## User & Access Management

### USER
**Description**: System users including employees, managers, and administrators
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| user_id | INT | PK, AUTO_INCREMENT | Unique user identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| email | VARCHAR(100) | UNIQUE, NOT NULL | User email |
| first_name | VARCHAR(50) | NOT NULL | First name |
| last_name | VARCHAR(50) | NOT NULL | Last name |
| password_hash | VARCHAR(255) | NOT NULL | Encrypted password |
| role_id | INT | FK → ROLE | User role |
| location_id | INT | FK → LOCATION | Assigned location |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| last_login | DATETIME | | Last login timestamp |
| created_date | DATETIME | NOT NULL | Account creation |
| created_by | INT | FK → USER | Creator user |

### ROLE
**Description**: User roles defining access levels
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| role_id | INT | PK, AUTO_INCREMENT | Unique role identifier |
| role_name | VARCHAR(50) | UNIQUE, NOT NULL | Role name |
| description | TEXT | | Role description |
| is_system_role | BOOLEAN | DEFAULT FALSE | System-defined role |
| created_date | DATETIME | NOT NULL | Creation date |

### USER_ROLE_PERMISSIONS
**Description**: Permissions assigned to roles
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| permission_id | INT | PK, AUTO_INCREMENT | Unique permission ID |
| role_id | INT | FK → ROLE | Associated role |
| permission_code | VARCHAR(50) | NOT NULL | Permission code |
| permission_type | VARCHAR(50) | | SALE_CREATE, RENTAL_CREATE, etc. |
| is_granted | BOOLEAN | DEFAULT TRUE | Permission status |

---

## Customer Management

### CUSTOMER
**Description**: Customer master data for individuals and businesses
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| customer_id | INT | PK, AUTO_INCREMENT | Unique customer ID |
| customer_code | VARCHAR(20) | UNIQUE | Business customer code |
| customer_type | ENUM | NOT NULL | INDIVIDUAL, BUSINESS |
| business_name | VARCHAR(200) | | Company name (if business) |
| first_name | VARCHAR(50) | | Individual first name |
| last_name | VARCHAR(50) | | Individual last name |
| email | VARCHAR(100) | | Primary email |
| mobile | VARCHAR(20) | NOT NULL | Primary phone |
| tax_id | VARCHAR(50) | | GST/Tax number |
| customer_tier | ENUM | | BRONZE, SILVER, GOLD, PLATINUM |
| credit_limit | DECIMAL(15,2) | DEFAULT 0 | Credit limit |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| blacklist_status | ENUM | DEFAULT 'CLEAR' | CLEAR, BLACKLISTED |
| created_date | DATETIME | NOT NULL | Registration date |
| last_transaction_date | DATETIME | | Last activity |
| lifetime_value | DECIMAL(15,2) | DEFAULT 0 | Total purchase value |

### CUSTOMER_CONTACT
**Description**: Additional contact persons for customers
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| contact_id | INT | PK, AUTO_INCREMENT | Unique contact ID |
| customer_id | INT | FK → CUSTOMER | Parent customer |
| contact_name | VARCHAR(100) | NOT NULL | Contact person name |
| designation | VARCHAR(50) | | Job title |
| mobile | VARCHAR(20) | | Contact phone |
| email | VARCHAR(100) | | Contact email |
| is_primary | BOOLEAN | DEFAULT FALSE | Primary contact flag |

### CUSTOMER_ADDRESS
**Description**: Customer addresses for billing and shipping
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| address_id | INT | PK, AUTO_INCREMENT | Unique address ID |
| customer_id | INT | FK → CUSTOMER | Parent customer |
| address_type | ENUM | NOT NULL | BILLING, SHIPPING, BOTH |
| address_line1 | VARCHAR(200) | NOT NULL | Address line 1 |
| address_line2 | VARCHAR(200) | | Address line 2 |
| city | VARCHAR(50) | NOT NULL | City |
| state | VARCHAR(50) | NOT NULL | State/Province |
| country | VARCHAR(50) | NOT NULL | Country |
| postal_code | VARCHAR(20) | | ZIP/Postal code |
| is_default | BOOLEAN | DEFAULT FALSE | Default address flag |

### CUSTOMER_VERIFICATION
**Description**: KYC and verification documents
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| verification_id | INT | PK, AUTO_INCREMENT | Unique verification ID |
| customer_id | INT | FK → CUSTOMER | Parent customer |
| document_type | VARCHAR(50) | NOT NULL | ID_PROOF, ADDRESS_PROOF, etc. |
| document_number | VARCHAR(100) | | Document number |
| document_path | VARCHAR(500) | | File storage path |
| verification_status | ENUM | | PENDING, VERIFIED, REJECTED |
| verified_by | INT | FK → USER | Verifying user |
| verified_date | DATETIME | | Verification date |
| expiry_date | DATE | | Document expiry |

### CUSTOMER_CREDIT
**Description**: Customer credit and payment terms
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| credit_id | INT | PK, AUTO_INCREMENT | Unique credit ID |
| customer_id | INT | FK → CUSTOMER | Parent customer |
| credit_limit | DECIMAL(15,2) | NOT NULL | Maximum credit |
| used_credit | DECIMAL(15,2) | DEFAULT 0 | Current usage |
| payment_terms | INT | DEFAULT 0 | Days for payment |
| credit_score | INT | | Internal credit score |
| last_review_date | DATE | | Last review date |

---

## Product & SKU Management

### CATEGORY
**Description**: Product categories and subcategories
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| category_id | INT | PK, AUTO_INCREMENT | Unique category ID |
| category_name | VARCHAR(100) | NOT NULL | Category name |
| parent_category_id | INT | FK → CATEGORY | Parent category |
| category_path | VARCHAR(500) | | Full category path |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

### BRAND
**Description**: Product brands
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| brand_id | INT | PK, AUTO_INCREMENT | Unique brand ID |
| brand_name | VARCHAR(100) | UNIQUE, NOT NULL | Brand name |
| brand_code | VARCHAR(20) | UNIQUE | Brand code |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

### ITEM_MASTER
**Description**: Master product definitions
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| item_id | INT | PK, AUTO_INCREMENT | Unique item ID |
| item_code | VARCHAR(50) | UNIQUE, NOT NULL | Item code |
| item_name | VARCHAR(200) | NOT NULL | Item name |
| category_id | INT | FK → CATEGORY | Product category |
| brand_id | INT | FK → BRAND | Product brand |
| item_type | ENUM | NOT NULL | PRODUCT, SERVICE, BUNDLE |
| is_serialized | BOOLEAN | DEFAULT FALSE | Requires serial tracking |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_date | DATETIME | NOT NULL | Creation date |

### SKU
**Description**: Stock Keeping Units - specific product variants
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| sku_id | INT | PK, AUTO_INCREMENT | Unique SKU ID |
| sku_code | VARCHAR(50) | UNIQUE, NOT NULL | SKU code |
| item_id | INT | FK → ITEM_MASTER | Parent item |
| sku_name | VARCHAR(200) | NOT NULL | SKU name |
| barcode | VARCHAR(50) | UNIQUE | Barcode/UPC |
| model_number | VARCHAR(100) | | Manufacturer model |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| is_rentable | BOOLEAN | DEFAULT FALSE | Available for rent |
| is_saleable | BOOLEAN | DEFAULT TRUE | Available for sale |
| min_rental_days | INT | DEFAULT 1 | Minimum rental period |
| max_rental_days | INT | | Maximum rental period |

### PRODUCT_ATTRIBUTES
**Description**: Product specifications and attributes
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| attribute_id | INT | PK, AUTO_INCREMENT | Unique attribute ID |
| sku_id | INT | FK → SKU | Parent SKU |
| attribute_name | VARCHAR(100) | NOT NULL | Attribute name |
| attribute_value | VARCHAR(500) | | Attribute value |
| attribute_type | VARCHAR(50) | | Type classification |
| display_order | INT | | Display sequence |

---

## Inventory Management

### INVENTORY_UNIT
**Description**: Individual inventory items (for serialized products)
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| inventory_id | VARCHAR(50) | PK | Unique inventory ID |
| sku_id | INT | FK → SKU | Product SKU |
| serial_number | VARCHAR(100) | UNIQUE | Serial number |
| location_id | INT | FK → LOCATION | Current location |
| current_status | ENUM | NOT NULL | See status values below |
| condition_grade | ENUM | | A, B, C, D |
| purchase_date | DATE | | Purchase date |
| purchase_cost | DECIMAL(15,2) | | Unit cost |
| current_customer | INT | FK → CUSTOMER | If rented/sold |
| last_inspection_date | DATE | | Last QC date |
| total_rental_days | INT | DEFAULT 0 | Lifetime rental days |
| created_date | DATETIME | NOT NULL | Entry date |

**Status Values**: AVAILABLE_SALE, AVAILABLE_RENT, RESERVED_SALE, RESERVED_RENT, RENTED, SOLD, IN_TRANSIT, INSPECTION_PENDING, CLEANING, REPAIR, DAMAGED, LOST

### STOCK_LEVEL
**Description**: Aggregate inventory levels by SKU and location
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| stock_id | INT | PK, AUTO_INCREMENT | Unique stock ID |
| sku_id | INT | FK → SKU | Product SKU |
| location_id | INT | FK → LOCATION | Stock location |
| total_quantity | INT | DEFAULT 0 | Total units |
| available_sale | INT | DEFAULT 0 | Available for sale |
| available_rent | INT | DEFAULT 0 | Available for rent |
| reserved | INT | DEFAULT 0 | Reserved units |
| in_transit | INT | DEFAULT 0 | Units in transit |
| damaged | INT | DEFAULT 0 | Damaged units |
| last_updated | DATETIME | | Last update time |

### INVENTORY_STATUS_HISTORY
**Description**: Track all inventory status changes
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| history_id | INT | PK, AUTO_INCREMENT | Unique history ID |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Inventory item |
| from_status | ENUM | | Previous status |
| to_status | ENUM | NOT NULL | New status |
| changed_by | INT | FK → USER | User making change |
| change_date | DATETIME | NOT NULL | Change timestamp |
| reason | VARCHAR(500) | | Change reason |
| transaction_id | INT | FK → TRANSACTION_HEADER | Related transaction |

### INVENTORY_HOLD
**Description**: Temporary inventory holds
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| hold_id | INT | PK, AUTO_INCREMENT | Unique hold ID |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Held item |
| hold_type | ENUM | NOT NULL | SALE, RENTAL, TRANSFER |
| hold_by | INT | FK → USER | User creating hold |
| customer_id | INT | FK → CUSTOMER | For customer |
| hold_start | DATETIME | NOT NULL | Hold start time |
| hold_expiry | DATETIME | NOT NULL | Hold expiration |
| is_active | BOOLEAN | DEFAULT TRUE | Hold status |

### RENTAL_CALENDAR
**Description**: Rental availability calendar
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| calendar_id | INT | PK, AUTO_INCREMENT | Unique calendar ID |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Inventory item |
| blocked_date | DATE | NOT NULL | Blocked date |
| transaction_id | INT | FK → TRANSACTION_HEADER | Related rental |
| block_type | ENUM | | RENTAL, MAINTENANCE, HOLD |

---

## Transaction Management

### TRANSACTION_HEADER
**Description**: Master transaction table for all transaction types
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| transaction_id | INT | PK, AUTO_INCREMENT | Unique transaction ID |
| transaction_number | VARCHAR(50) | UNIQUE, NOT NULL | Business transaction # |
| transaction_type | ENUM | NOT NULL | SALE, RENTAL, RETURN, PURCHASE |
| transaction_date | DATETIME | NOT NULL | Transaction timestamp |
| customer_id | INT | FK → CUSTOMER | Customer |
| user_id | INT | FK → USER | Transaction user |
| location_id | INT | FK → LOCATION | Transaction location |
| status | ENUM | NOT NULL | IN_PROCESS, CONFIRMED, COMPLETED, CANCELLED |
| subtotal_amount | DECIMAL(15,2) | | Before tax/discount |
| discount_amount | DECIMAL(15,2) | DEFAULT 0 | Total discount |
| tax_amount | DECIMAL(15,2) | DEFAULT 0 | Total tax |
| total_amount | DECIMAL(15,2) | NOT NULL | Final amount |
| payment_status | ENUM | | PENDING, PARTIAL, PAID |
| payment_terms | VARCHAR(50) | | Payment terms |
| notes | TEXT | | Transaction notes |
| created_date | DATETIME | NOT NULL | Creation timestamp |
| modified_date | DATETIME | | Last modification |

### TRANSACTION_LINE
**Description**: Line items for each transaction
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| line_id | INT | PK, AUTO_INCREMENT | Unique line ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Parent transaction |
| line_number | INT | NOT NULL | Line sequence |
| sku_id | INT | FK → SKU | Product SKU |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Specific unit (if serialized) |
| quantity | DECIMAL(10,2) | NOT NULL | Quantity |
| unit_price | DECIMAL(15,2) | NOT NULL | Price per unit |
| discount_percent | DECIMAL(5,2) | DEFAULT 0 | Line discount % |
| discount_amount | DECIMAL(15,2) | DEFAULT 0 | Line discount amount |
| tax_rate | DECIMAL(5,2) | DEFAULT 0 | Tax rate |
| tax_amount | DECIMAL(15,2) | DEFAULT 0 | Tax amount |
| line_total | DECIMAL(15,2) | NOT NULL | Line total |
| notes | TEXT | | Line notes |

### RENTAL_TRANSACTION_DETAILS
**Description**: Additional details specific to rental transactions
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| rental_detail_id | INT | PK, AUTO_INCREMENT | Unique detail ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Parent transaction |
| rental_start_date | DATETIME | NOT NULL | Rental start |
| rental_end_date | DATETIME | NOT NULL | Rental end |
| actual_return_date | DATETIME | | Actual return |
| deposit_amount | DECIMAL(15,2) | | Security deposit |
| insurance_type | ENUM | | NONE, BASIC, COMPREHENSIVE |
| insurance_amount | DECIMAL(15,2) | | Insurance fee |
| late_fee | DECIMAL(15,2) | DEFAULT 0 | Late return fee |
| damage_fee | DECIMAL(15,2) | DEFAULT 0 | Damage charges |

---

## Pricing & Discount Management

### PRICE_LIST
**Description**: Named price lists for different customer segments
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| price_list_id | INT | PK, AUTO_INCREMENT | Unique price list ID |
| price_list_name | VARCHAR(100) | NOT NULL | Price list name |
| currency_code | VARCHAR(3) | DEFAULT 'INR' | Currency |
| is_default | BOOLEAN | DEFAULT FALSE | Default list |
| valid_from | DATE | | Effective from |
| valid_to | DATE | | Effective until |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

### PRICE_LIST_ITEM
**Description**: SKU prices in each price list
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| price_item_id | INT | PK, AUTO_INCREMENT | Unique price item ID |
| price_list_id | INT | FK → PRICE_LIST | Parent price list |
| sku_id | INT | FK → SKU | Product SKU |
| unit_price | DECIMAL(15,2) | NOT NULL | Selling price |
| min_quantity | DECIMAL(10,2) | DEFAULT 1 | Minimum quantity |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

### RENTAL_PRICE_MASTER
**Description**: Rental pricing by SKU
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| rental_price_id | INT | PK, AUTO_INCREMENT | Unique rental price ID |
| sku_id | INT | FK → SKU | Product SKU |
| daily_rate | DECIMAL(15,2) | NOT NULL | Per day rate |
| weekly_rate | DECIMAL(15,2) | | 7-day rate |
| monthly_rate | DECIMAL(15,2) | | 30-day rate |
| weekend_surcharge | DECIMAL(15,2) | DEFAULT 0 | Weekend extra |
| peak_season_surcharge | DECIMAL(5,2) | DEFAULT 0 | Peak season % |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

### CUSTOMER_DISCOUNT
**Description**: Customer-specific discounts
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| discount_id | INT | PK, AUTO_INCREMENT | Unique discount ID |
| customer_id | INT | FK → CUSTOMER | Customer |
| discount_type | ENUM | | PERCENTAGE, FIXED_AMOUNT |
| discount_value | DECIMAL(15,2) | NOT NULL | Discount value |
| valid_from | DATE | | Start date |
| valid_to | DATE | | End date |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

---

## Payment & Financial Management

### PAYMENT
**Description**: All payment transactions
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| payment_id | INT | PK, AUTO_INCREMENT | Unique payment ID |
| payment_number | VARCHAR(50) | UNIQUE | Payment reference |
| transaction_id | INT | FK → TRANSACTION_HEADER | Related transaction |
| payment_date | DATETIME | NOT NULL | Payment timestamp |
| payment_method | ENUM | NOT NULL | CASH, CARD, BANK_TRANSFER, UPI |
| amount | DECIMAL(15,2) | NOT NULL | Payment amount |
| reference_number | VARCHAR(100) | | External reference |
| payment_status | ENUM | | PENDING, VERIFIED, FAILED |
| verified_by | INT | FK → USER | Verifying user |
| notes | TEXT | | Payment notes |

### DEPOSIT_TRANSACTION
**Description**: Security deposits for rentals
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| deposit_id | INT | PK, AUTO_INCREMENT | Unique deposit ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Rental transaction |
| deposit_amount | DECIMAL(15,2) | NOT NULL | Deposit amount |
| payment_id | INT | FK → PAYMENT | Deposit payment |
| status | ENUM | | HELD, PARTIALLY_REFUNDED, FULLY_REFUNDED |
| refund_amount | DECIMAL(15,2) | | Refunded amount |
| refund_date | DATETIME | | Refund date |
| deduction_reason | TEXT | | If deducted |

### REFUND_PROCESSING
**Description**: Refund transactions
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| refund_id | INT | PK, AUTO_INCREMENT | Unique refund ID |
| original_payment_id | INT | FK → PAYMENT | Original payment |
| refund_amount | DECIMAL(15,2) | NOT NULL | Refund amount |
| refund_method | ENUM | | SAME_AS_ORIGINAL, CASH, BANK_TRANSFER |
| refund_status | ENUM | | INITIATED, PROCESSING, COMPLETED |
| initiated_date | DATETIME | NOT NULL | Initiation time |
| completed_date | DATETIME | | Completion time |
| initiated_by | INT | FK → USER | Initiating user |

---

## Rental-Specific Tables

### RENTAL_RESERVATION
**Description**: Rental bookings and reservations
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| reservation_id | INT | PK, AUTO_INCREMENT | Unique reservation ID |
| reservation_number | VARCHAR(50) | UNIQUE | Reservation code |
| customer_id | INT | FK → CUSTOMER | Customer |
| created_date | DATETIME | NOT NULL | Booking time |
| expiry_date | DATETIME | | Hold expiration |
| status | ENUM | | PENDING, CONFIRMED, CONVERTED, EXPIRED |
| converted_transaction_id | INT | FK → TRANSACTION_HEADER | If converted |

### RENTAL_AGREEMENT
**Description**: Legal rental agreements
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| agreement_id | INT | PK, AUTO_INCREMENT | Unique agreement ID |
| agreement_number | VARCHAR(50) | UNIQUE | Agreement number |
| transaction_id | INT | FK → TRANSACTION_HEADER | Rental transaction |
| agreement_date | DATETIME | NOT NULL | Agreement date |
| terms_version | VARCHAR(20) | | Terms version |
| customer_signature | TEXT | | Digital signature |
| staff_signature | TEXT | | Staff signature |
| agreement_pdf_path | VARCHAR(500) | | PDF location |

### RENTAL_EXTENSION
**Description**: Rental period extensions
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| extension_id | INT | PK, AUTO_INCREMENT | Unique extension ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Original rental |
| original_end_date | DATETIME | NOT NULL | Original due date |
| new_end_date | DATETIME | NOT NULL | Extended date |
| extension_days | INT | NOT NULL | Additional days |
| additional_charge | DECIMAL(15,2) | | Extension fee |
| approved_by | INT | FK → USER | Approving user |
| extension_date | DATETIME | NOT NULL | Extension timestamp |

---

## Sales-Specific Tables

### SALES_COMMISSION
**Description**: Sales commission calculations
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| commission_id | INT | PK, AUTO_INCREMENT | Unique commission ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Sale transaction |
| user_id | INT | FK → USER | Salesperson |
| commission_rate | DECIMAL(5,2) | | Commission % |
| commission_amount | DECIMAL(15,2) | NOT NULL | Commission amount |
| status | ENUM | | CALCULATED, APPROVED, PAID |
| payment_date | DATE | | Payment date |

### WARRANTY_ACTIVATION
**Description**: Product warranty records
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| warranty_id | INT | PK, AUTO_INCREMENT | Unique warranty ID |
| transaction_line_id | INT | FK → TRANSACTION_LINE | Sale line item |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Product unit |
| warranty_start_date | DATE | NOT NULL | Start date |
| warranty_end_date | DATE | NOT NULL | End date |
| warranty_type | ENUM | | MANUFACTURER, EXTENDED |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |

---

## Document Management

### INVOICE
**Description**: Sales and rental invoices
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| invoice_id | INT | PK, AUTO_INCREMENT | Unique invoice ID |
| invoice_number | VARCHAR(50) | UNIQUE, NOT NULL | Invoice number |
| transaction_id | INT | FK → TRANSACTION_HEADER | Transaction |
| invoice_date | DATETIME | NOT NULL | Invoice date |
| due_date | DATE | | Payment due date |
| invoice_type | ENUM | | SALES, RENTAL, CREDIT_NOTE |
| total_amount | DECIMAL(15,2) | NOT NULL | Invoice total |
| pdf_path | VARCHAR(500) | | PDF location |
| is_sent | BOOLEAN | DEFAULT FALSE | Sent to customer |

### DELIVERY_NOTE
**Description**: Delivery/pickup documentation
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| delivery_note_id | INT | PK, AUTO_INCREMENT | Unique delivery ID |
| delivery_number | VARCHAR(50) | UNIQUE | Delivery number |
| transaction_id | INT | FK → TRANSACTION_HEADER | Transaction |
| delivery_type | ENUM | | DELIVERY, PICKUP, RETURN |
| scheduled_date | DATETIME | | Scheduled time |
| actual_date | DATETIME | | Actual time |
| delivered_by | INT | FK → USER | Delivery person |
| received_by | VARCHAR(100) | | Recipient name |
| signature_path | VARCHAR(500) | | Signature image |

---

## Inspection & Quality Control

### PRE_RENTAL_INSPECTION
**Description**: Inspection before rental handover
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| inspection_id | INT | PK, AUTO_INCREMENT | Unique inspection ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Rental transaction |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Item inspected |
| inspection_date | DATETIME | NOT NULL | Inspection time |
| inspector_id | INT | FK → USER | Inspector |
| condition_grade | ENUM | | A, B, C, D |
| checklist_completed | BOOLEAN | DEFAULT FALSE | Checklist done |
| notes | TEXT | | Condition notes |
| customer_acknowledged | BOOLEAN | DEFAULT FALSE | Customer agreed |

### POST_RENTAL_INSPECTION
**Description**: Inspection after rental return
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| inspection_id | INT | PK, AUTO_INCREMENT | Unique inspection ID |
| transaction_id | INT | FK → TRANSACTION_HEADER | Rental transaction |
| inventory_id | VARCHAR(50) | FK → INVENTORY_UNIT | Item inspected |
| inspection_date | DATETIME | NOT NULL | Inspection time |
| inspector_id | INT | FK → USER | Inspector |
| condition_grade | ENUM | | A, B, C, D |
| damage_found | BOOLEAN | DEFAULT FALSE | Damage flag |
| cleaning_required | BOOLEAN | DEFAULT FALSE | Needs cleaning |
| repair_required | BOOLEAN | DEFAULT FALSE | Needs repair |

### DAMAGE_ASSESSMENT
**Description**: Damage documentation and costing
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| damage_id | INT | PK, AUTO_INCREMENT | Unique damage ID |
| inspection_id | INT | FK → POST_RENTAL_INSPECTION | Related inspection |
| damage_type | ENUM | | COSMETIC, FUNCTIONAL, TOTAL_LOSS |
| damage_description | TEXT | NOT NULL | Damage details |
| repair_cost_estimate | DECIMAL(15,2) | | Repair estimate |
| customer_liable | BOOLEAN | DEFAULT TRUE | Customer liability |
| charge_amount | DECIMAL(15,2) | | Actual charge |
| insurance_covered | BOOLEAN | DEFAULT FALSE | Insurance coverage |

### INSPECTION_PHOTOS
**Description**: Photos taken during inspections
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| photo_id | INT | PK, AUTO_INCREMENT | Unique photo ID |
| inspection_id | INT | | Related inspection |
| inspection_type | ENUM | | PRE_RENTAL, POST_RENTAL |
| photo_path | VARCHAR(500) | NOT NULL | File path |
| photo_type | VARCHAR(50) | | OVERALL, DAMAGE, SERIAL |
| upload_date | DATETIME | NOT NULL | Upload time |

---

## Analytics & Reporting

### DAILY_SALES_SUMMARY
**Description**: Aggregated daily sales metrics
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| summary_id | INT | PK, AUTO_INCREMENT | Unique summary ID |
| summary_date | DATE | NOT NULL | Summary date |
| location_id | INT | FK → LOCATION | Location |
| total_transactions | INT | | Transaction count |
| total_revenue | DECIMAL(15,2) | | Revenue amount |
| total_units_sold | INT | | Units sold |
| total_customers | INT | | Unique customers |

### RENTAL_ANALYTICS_SUMMARY
**Description**: Rental performance metrics
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| summary_id | INT | PK, AUTO_INCREMENT | Unique summary ID |
| summary_date | DATE | NOT NULL | Summary date |
| total_rentals | INT | | Rental count |
| total_revenue | DECIMAL(15,2) | | Rental revenue |
| average_duration | DECIMAL(5,2) | | Avg rental days |
| on_time_return_rate | DECIMAL(5,2) | | % on-time returns |
| damage_rate | DECIMAL(5,2) | | % with damage |

### INVENTORY_TURNOVER
**Description**: Inventory movement analytics
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| turnover_id | INT | PK, AUTO_INCREMENT | Unique turnover ID |
| sku_id | INT | FK → SKU | Product SKU |
| period_month | DATE | NOT NULL | Month |
| units_sold | INT | | Sales quantity |
| units_rented | INT | | Rental quantity |
| turnover_ratio | DECIMAL(5,2) | | Turnover rate |
| average_days_to_sell | INT | | Avg sale time |

---

## System Configuration

### SYSTEM_PARAMETER
**Description**: System-wide configuration parameters
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| parameter_id | INT | PK, AUTO_INCREMENT | Unique parameter ID |
| parameter_name | VARCHAR(100) | UNIQUE, NOT NULL | Parameter name |
| parameter_value | VARCHAR(500) | | Parameter value |
| parameter_type | VARCHAR(50) | | STRING, NUMBER, BOOLEAN |
| description | TEXT | | Parameter description |
| is_editable | BOOLEAN | DEFAULT TRUE | Can be modified |

### NUMBER_SEQUENCE
**Description**: Auto-numbering sequences
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| sequence_id | INT | PK, AUTO_INCREMENT | Unique sequence ID |
| sequence_name | VARCHAR(50) | UNIQUE | Sequence name |
| prefix | VARCHAR(20) | | Number prefix |
| current_number | INT | NOT NULL | Current value |
| increment_by | INT | DEFAULT 1 | Increment value |
| min_digits | INT | DEFAULT 4 | Minimum digits |

### AUDIT_LOG
**Description**: System-wide audit trail
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| audit_id | BIGINT | PK, AUTO_INCREMENT | Unique audit ID |
| table_name | VARCHAR(100) | NOT NULL | Affected table |
| record_id | VARCHAR(100) | NOT NULL | Affected record |
| action | ENUM | NOT NULL | INSERT, UPDATE, DELETE |
| user_id | INT | FK → USER | User performing action |
| action_date | DATETIME | NOT NULL | Action timestamp |
| old_values | JSON | | Previous values |
| new_values | JSON | | New values |
| ip_address | VARCHAR(45) | | User IP |

### TAX_CONFIGURATION
**Description**: Tax rates and rules
| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| tax_id | INT | PK, AUTO_INCREMENT | Unique tax ID |
| tax_name | VARCHAR(50) | NOT NULL | Tax name (GST, VAT) |
| tax_rate | DECIMAL(5,2) | NOT NULL | Tax percentage |
| category_id | INT | FK → CATEGORY | Product category |
| effective_from | DATE | NOT NULL | Start date |
| effective_to | DATE | | End date |

---

## Entity Relationship Summary

### Primary Relationships

1. **Customer → Transaction**
   - One customer can have many transactions (sales, rentals)
   - Relationship: CUSTOMER.customer_id → TRANSACTION_HEADER.customer_id

2. **Transaction → Transaction Lines**
   - One transaction has multiple line items
   - Relationship: TRANSACTION_HEADER.transaction_id → TRANSACTION_LINE.transaction_id

3. **SKU → Inventory Unit**
   - One SKU can have many inventory units (for serialized items)
   - Relationship: SKU.sku_id → INVENTORY_UNIT.sku_id

4. **Transaction → Payment**
   - One transaction can have multiple payments
   - Relationship: TRANSACTION_HEADER.transaction_id → PAYMENT.transaction_id

5. **Inventory Unit → Status History**
   - One inventory unit has many status changes
   - Relationship: INVENTORY_UNIT.inventory_id → INVENTORY_STATUS_HISTORY.inventory_id

6. **User → Location**
   - Users are assigned to locations
   - Relationship: LOCATION.location_id → USER.location_id

7. **Rental Transaction → Inspections**
   - One rental has pre and post inspections
   - Relationship: TRANSACTION_HEADER.transaction_id → PRE/POST_RENTAL_INSPECTION.transaction_id

### Key Business Rules

1. **Inventory Status Flow**:
   - Sale: AVAILABLE_SALE → RESERVED_SALE → SOLD
   - Rental: AVAILABLE_RENT → RESERVED_RENT → RENTED → INSPECTION_PENDING → AVAILABLE_RENT

2. **Transaction Types**:
   - SALE: Direct sale transactions
   - RENTAL: Rental transactions with return cycle
   - RETURN: Rental return processing
   - PURCHASE: Inventory procurement

3. **Payment Flows**:
   - Sales: Full payment required
   - Rentals: Rental fee + refundable deposit
   - Returns: Deposit refund minus deductions

4. **Inspection Requirements**:
   - Pre-rental: Mandatory before handover
   - Post-rental: Mandatory before deposit settlement

5. **Serial Tracking**:
   - Serialized items: Individual INVENTORY_UNIT records
   - Non-serialized: Quantity tracking in STOCK_LEVEL only

This data model supports a comprehensive inventory management system handling both sales and rental operations with complete traceability, financial management, and customer relationship tracking.