# Detailed Sales Transaction Process Documentation

## Overview

This document provides a comprehensive guide to the sales transaction process for direct, final sales without intermediate stages. All sales are considered completed at the point of transaction, suitable for retail counter sales, B2B sales, and online order fulfillment.

---

## 1. Sales Initiation and User Verification

### Description

System validates the salesperson's credentials and prepares the sales environment with appropriate permissions and configurations.

### Process Steps and Database Operations

#### 1.1 Salesperson Authentication

**Description**: Verify user has sales transaction permissions

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| USER | READ | Validate salesperson credentials | `SELECT * FROM USER WHERE username = 'sales.exec01'` returns user_id: 102 |
| USER_ROLE_PERMISSIONS | READ | Check sales permissions | Role has 'SALE_CREATE' and 'DISCOUNT_APPLY' permissions |
| SALES_COMMISSION_SETUP | READ | Get commission structure | 2% on electronics, 3% on accessories |
| LOCATION | READ | Get assigned store/warehouse | User assigned to Store location_id: 2 |

#### 1.2 Sales Configuration Load

**Description**: Load sales-related settings and rules

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| SYSTEM_PARAMETER | READ | Get sales configurations | Min margin: 15%, Max discount: 20% |
| TAX_CONFIGURATION | READ | Load applicable tax rates | GST: 18% electronics, 12% accessories |
| PAYMENT_METHOD_CONFIG | READ | Available payment options | Cash, Card, UPI, Bank Transfer enabled |
| SALES_POLICY | READ | Active sales policies | Return policy: 7 days, Exchange: 15 days |

**Example Scenario**:
Sales executive preparing to sell 2 HP laptops and 3 Dell monitors to a corporate customer who walked into the store.

---

## 2. Customer Identification and Verification

### Description

Identify the customer, verify their purchase eligibility, and check for any special pricing or restrictions.

### Process Steps and Database Operations

#### 2.1 Customer Search

**Description**: Look up existing customer or create new record

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| CUSTOMER | READ | Search customer database | Found "Sharma Electronics Pvt Ltd" customer_id: 3001 |
| CUSTOMER_CONTACT | READ | Get contact details | Primary: Mr. Sharma, Mobile: 9876543210 |
| CUSTOMER_CREDIT | READ | Check credit status | Credit limit: ₹5,00,000, Used: ₹1,50,000 |
| CUSTOMER_TYPE | READ | Customer classification | Type: B2B, Tier: Gold, Since: 2020 |

#### 2.2 Create New Customer (if needed)

**Description**: Register new customer in the system

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| CUSTOMER | INSERT | Create customer record | New customer "TechStart Solutions" |
| CUSTOMER_VERIFICATION | INSERT | KYC documentation | GST: 27AABCT1234F1ZH, PAN provided |
| CUSTOMER_ADDRESS | INSERT | Billing/shipping addresses | Registered office and delivery addresses |
| AUDIT_LOG | INSERT | Log customer creation | User 102 created customer at 14:30:00 |

#### 2.3 Customer Eligibility Check

**Description**: Verify customer can make the purchase

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| CUSTOMER_BLACKLIST | READ | Check restrictions | Status: CLEAR, No restrictions |
| OUTSTANDING_PAYMENTS | READ | Check overdue amounts | No overdue payments |
| CUSTOMER_PURCHASE_HISTORY | READ | Purchase patterns | 15 purchases, ₹25,00,000 lifetime value |
| SPECIAL_PRICING_AGREEMENT | READ | Custom pricing check | 5% corporate discount applicable |

---

## 3. Product Selection and Availability Verification

### Description

Search for products, check availability, and ensure items are in saleable condition.

### Process Steps and Database Operations

#### 3.1 Product Search

**Description**: Find products customer wants to purchase

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| SKU | READ | Search product catalog | Found: HP ProBook 450, Dell 24" Monitor |
| ITEM_MASTER | READ | Get product details | Categories: Laptops, Monitors |
| PRODUCT_ATTRIBUTES | READ | Product specifications | HP: 15.6", i5, 8GB RAM; Dell: 24", FHD, IPS |
| PRODUCT_IMAGES | READ | Display images | Show product photos to customer |

#### 3.2 Availability Check

**Description**: Verify items are available for sale

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| INVENTORY_UNIT | READ | Find saleable units | HP: 5 units in 'AVAILABLE_SALE' status |
| STOCK_LEVEL | READ | Check aggregate stock | Dell Monitor: 10 available for sale |
| LOCATION_INVENTORY | READ | Location-specific stock | Store 2: HP(3), Dell(10) available |
| HOLD_ITEMS | READ | Check for holds | No items on hold |

**Availability Example**:

```
HP ProBook 450:
- Total in location: 5 units
- Available for sale: 5 units
- Serial numbers: HP2025-001 to HP2025-005

Dell 24" Monitor:
- Total in location: 10 units
- Available for sale: 10 units
- Non-serialized batch: BATCH-MON-2025-01
```

#### 3.3 Product Reservation

**Description**: Temporarily reserve items during sale process

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| INVENTORY_HOLD | INSERT | Create temporary hold | Hold 2 HP laptops for 30 minutes |
| HOLD_EXPIRY_QUEUE | INSERT | Auto-release timer | Release at 15:00 if not confirmed |
| AVAILABILITY_UPDATE | UPDATE | Update real-time availability | HP available: 5 → 3 (2 on hold) |

---

## 4. Pricing Calculation and Discounts

### Description

Calculate product prices, apply discounts, and determine final sale amount.

### Process Steps and Database Operations

#### 4.1 Base Pricing Retrieval

**Description**: Get standard selling prices

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| PRICE_LIST | READ | Get active price list | Default Retail Price List active |
| PRICE_LIST_ITEM | READ | SKU-specific prices | HP: ₹55,000, Dell: ₹15,000 |
| COST_MASTER | READ | Get item costs | HP cost: ₹45,000, Dell: ₹12,000 |
| MARGIN_CALCULATION | INSERT | Calculate margins | HP margin: 22%, Dell: 25% |

#### 4.2 Discount Application

**Description**: Apply applicable discounts

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| CUSTOMER_DISCOUNT | READ | Customer-specific discount | 5% corporate discount |
| PROMOTIONAL_DISCOUNT | READ | Active promotions | None applicable |
| VOLUME_DISCOUNT | READ | Quantity-based discount | No volume discount for this quantity |
| DISCOUNT_AUTHORIZATION | INSERT | Approval for discounts | Auto-approved (within limits) |

**Pricing Calculation Example**:

```
HP ProBook (2 units):
- Unit price: ₹55,000
- Subtotal: ₹1,10,000
- Corporate discount (5%): -₹5,500
- Net: ₹1,04,500

Dell Monitor (3 units):
- Unit price: ₹15,000
- Subtotal: ₹45,000
- Corporate discount (5%): -₹2,250
- Net: ₹42,750

Total before tax: ₹1,47,250
```

#### 4.3 Tax Calculation

**Description**: Calculate applicable taxes

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| TAX_RULES | READ | Get tax rates | Interstate GST: 18% laptops, 18% monitors |
| TAX_CALCULATION | INSERT | Store calculations | IGST: ₹26,505 |
| TAX_EXEMPTION | READ | Check exemptions | No exemptions applicable |

---

## 5. Create Sales Transaction

### Description

Create the formal sales transaction with all details.

### Process Steps and Database Operations

#### 5.1 Create Transaction Header

**Description**: Initialize main sales record

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| TRANSACTION_HEADER | INSERT | Create sales record | Transaction #SALE-2025-0001 |
| NUMBER_SEQUENCE | UPDATE | Increment counter | Next: SALE-2025-0002 |
| SALES_METADATA | INSERT | Additional sale info | Walk-in sale, immediate delivery |

**Transaction Header Example**:

```
transaction_id: 6001
transaction_number: SALE-2025-0001
transaction_type: SALE
customer_id: 3001
transaction_date: 2025-01-20 14:45:00
salesperson_id: 102
location_id: 2
total_amount: 1,73,755
discount_amount: 7,750
tax_amount: 26,505
net_amount: 1,73,755
payment_terms: IMMEDIATE
status: IN_PROCESS
```

#### 5.2 Create Transaction Lines

**Description**: Add line items for each product

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| TRANSACTION_LINE | INSERT | Product line items | Line 1: HP laptops, Line 2: Dell monitors |
| LINE_SERIAL_NUMBERS | INSERT | Link serials to lines | HP2025-001, HP2025-002 to Line 1 |
| LINE_DISCOUNT_DETAIL | INSERT | Discount breakdown | 5% corporate discount per line |

**Line Items Example**:

```
Line 1:
- sku_id: 1001 (HP ProBook)
- quantity: 2
- unit_price: 55,000
- discount: 5,500
- tax: 18,810
- line_total: 1,23,310

Line 2:
- sku_id: 1002 (Dell Monitor)
- quantity: 3
- unit_price: 15,000
- discount: 2,250
- tax: 7,695
- line_total: 50,445
```

#### 5.3 Reserve Inventory

**Description**: Lock selected inventory units

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| INVENTORY_UNIT | UPDATE | Reserve items | Status: AVAILABLE_SALE → RESERVED_SALE |
| INVENTORY_STATUS_HISTORY | INSERT | Log status change | 5 items reserved for SALE-2025-0001 |
| SERIAL_ASSIGNMENT | INSERT | Assign serials | HP2025-001, HP2025-002 assigned |

---

## 6. Payment Processing

### Description

Handle customer payment through various payment methods.

### Process Steps and Database Operations

#### 6.1 Payment Method Selection

**Description**: Customer chooses payment method

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| PAYMENT_METHOD_SELECTION | INSERT | Record chosen method | Bank Transfer selected |
| PAYMENT_TERMS_CHECK | READ | Verify terms allowed | Immediate payment required |
| CREDIT_APPROVAL | READ | Check if credit allowed | Credit sales allowed for this customer |

#### 6.2 Process Payment

**Description**: Record payment details

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| PAYMENT | INSERT | Create payment record | Payment #PAY-2025-0001 |
| BANK_TRANSFER_DETAIL | INSERT | Transfer specifics | UTR: HDFC202501201234 |
| PAYMENT_VERIFICATION | INSERT | Verify payment | Amount verified: ₹1,73,755 |
| TRANSACTION_HEADER | UPDATE | Update payment status | payment_status: PAID |

**Payment Example**:

```
payment_id: 25001
transaction_id: 6001
payment_date: 2025-01-20 15:00:00
payment_method: BANK_TRANSFER
amount: 1,73,755
reference_number: HDFC202501201234
verification_status: VERIFIED
```

#### 6.3 Alternative Payment Handling

**Description**: Handle credit sales if applicable

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| CREDIT_SALES | INSERT | Record credit terms | Due in 30 days |
| ACCOUNTS_RECEIVABLE | INSERT | Create receivable | AR entry for ₹1,73,755 |
| CREDIT_LIMIT_UPDATE | UPDATE | Reduce available credit | Available: ₹3,50,000 → ₹1,76,245 |

---

## 7. Finalize Sale and Update Inventory

### Description

Complete the sale transaction and permanently update inventory status.

### Process Steps and Database Operations

#### 7.1 Confirm Sale

**Description**: Finalize the sale transaction

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| TRANSACTION_HEADER | UPDATE | Complete transaction | Status: IN_PROCESS → COMPLETED |
| SALES_CONFIRMATION | INSERT | Confirmation record | Confirmed by user 102 at 15:05:00 |
| INVENTORY_HOLD | DELETE | Release temporary holds | Clear holds on sold items |

#### 7.2 Update Inventory Status

**Description**: Mark items as sold

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| INVENTORY_UNIT | UPDATE | Final status update | Status: RESERVED_SALE → SOLD |
| INVENTORY_STATUS_HISTORY | INSERT | Final status log | 5 items marked as SOLD |
| SOLD_ITEMS_REGISTER | INSERT | Permanent record | Items removed from available inventory |
| WARRANTY_ACTIVATION | INSERT | Start warranty period | Warranty active until Jan 2026 |

**Inventory Update Example**:

```
HP Laptops:
- HP2025-001: AVAILABLE_SALE → SOLD
- HP2025-002: AVAILABLE_SALE → SOLD
- Customer: 3001
- Warranty: 12 months from today

Dell Monitors:
- Batch quantity: 10 → 7
- 3 units sold from BATCH-MON-2025-01
```

---

## 8. Generate Sales Documents

### Description

Create all required sales documentation including invoices and receipts.

### Process Steps and Database Operations

#### 8.1 Generate Sales Invoice

**Description**: Create tax invoice for the sale

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| INVOICE | INSERT | Create sales invoice | Invoice #SINV-2025-0001 |
| INVOICE_LINE | INSERT | Invoice line items | Detailed product breakdown |
| TAX_INVOICE_DETAIL | INSERT | Tax computation | GST details with HSN codes |
| INVOICE_NUMBER_SERIES | UPDATE | Increment invoice number | Next: SINV-2025-0002 |

**Invoice Example**:

```
Invoice: SINV-2025-0001
Date: 20-Jan-2025
Customer: Sharma Electronics Pvt Ltd
GSTIN: 27AABCS1234F1ZH

Items:
1. HP ProBook 450 (HSN: 8471)
   Qty: 2, Rate: 55,000, Discount: 5%
   Taxable: 1,04,500, IGST 18%: 18,810
   
2. Dell 24" Monitor (HSN: 8528)
   Qty: 3, Rate: 15,000, Discount: 5%
   Taxable: 42,750, IGST 18%: 7,695

Total: ₹1,73,755
```

#### 8.2 Generate Additional Documents

**Description**: Create supporting documents

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| DELIVERY_NOTE | INSERT | Delivery document | DN-2025-0001 for logistics |
| WARRANTY_CARD | INSERT | Warranty documents | 5 warranty cards generated |
| RECEIPT | INSERT | Payment receipt | Receipt for ₹1,73,755 |
| DOCUMENT_PRINTING_QUEUE | INSERT | Queue for printing | 4 documents queued |

---

## 9. Update Stock Levels and Analytics

### Description

Update system-wide stock levels and analytical data.

### Process Steps and Database Operations

#### 9.1 Stock Level Updates

**Description**: Decrease available inventory

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| STOCK_LEVEL | UPDATE | Reduce quantities | HP: 10→8, Dell: 15→12 |
| STOCK_MOVEMENT | INSERT | Record movement | -2 HP, -3 Dell, reason: SALE |
| LOCATION_STOCK | UPDATE | Location-specific | Store 2 stock updated |
| CHANNEL_INVENTORY | UPDATE | Multi-channel sync | Online inventory updated |

**Stock Update Example**:

```
HP ProBook 450:
- Previous: 10 total (5 sale, 5 rent)
- Sold: 2 units
- Current: 8 total (3 sale, 5 rent)

Dell Monitor:
- Previous: 15 total (all for sale)
- Sold: 3 units
- Current: 12 total (all for sale)
```

#### 9.2 Reorder Point Check

**Description**: Check if reorder needed

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| REORDER_POINT_CHECK | READ | Check thresholds | HP below reorder point |
| REORDER_ALERT | INSERT | Create alert | Alert: HP ProBook low stock |
| PURCHASE_SUGGESTION | INSERT | Suggest reorder | Suggest order 10 units |

---

## 10. Financial Processing

### Description

Update financial records and calculate commissions.

### Process Steps and Database Operations

#### 10.1 Revenue Recognition

**Description**: Record sales revenue

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| REVENUE_RECOGNITION | INSERT | Record revenue | Revenue: ₹1,47,250 |
| COST_OF_GOODS_SOLD | INSERT | Record COGS | COGS: ₹1,14,000 |
| GROSS_PROFIT | INSERT | Calculate profit | Gross profit: ₹33,250 |
| GL_POSTING | INSERT | Accounting entries | Debit AR, Credit Revenue |

#### 10.2 Commission Calculation

**Description**: Calculate sales commissions

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| SALES_COMMISSION | INSERT | Commission record | 2% on laptops, 3% on monitors |
| COMMISSION_DETAIL | INSERT | Breakdown | Laptops: ₹2,200, Monitors: ₹1,350 |
| PAYROLL_QUEUE | INSERT | Queue for payment | Total commission: ₹3,550 |

**Commission Example**:

```
Salesperson: 102
HP Laptops: ₹1,10,000 × 2% = ₹2,200
Dell Monitors: ₹45,000 × 3% = ₹1,350
Total Commission: ₹3,550
```

---

## 11. Customer Updates

### Description

Update customer records and loyalty programs.

### Process Steps and Database Operations

#### 11.1 Customer Profile Update

**Description**: Update purchase history and metrics

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| CUSTOMER | UPDATE | Update last purchase | Last purchase: Jan 20, 2025 |
| CUSTOMER_PURCHASE_HISTORY | INSERT | Add to history | Purchase #16, amount: ₹1,73,755 |
| CUSTOMER_METRICS | UPDATE | Lifetime value | LTV: ₹25,00,000 → ₹26,73,755 |
| CUSTOMER_CATEGORY_PURCHASE | INSERT | Category tracking | Laptops: 2, Monitors: 3 |

#### 11.2 Loyalty Program

**Description**: Award loyalty points

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| LOYALTY_POINTS | INSERT | Award points | 1,737 points (₹100 = 1 point) |
| LOYALTY_BALANCE | UPDATE | Update balance | Balance: 5,000 → 6,737 points |
| TIER_EVALUATION | INSERT | Check tier upgrade | Remains in Gold tier |

---

## 12. Post-Sale Processes

### Description

Trigger various post-sale activities and notifications.

### Process Steps and Database Operations

#### 12.1 Delivery/Pickup Management

**Description**: Arrange item handover

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| DELIVERY_REQUEST | INSERT | Create delivery task | Immediate store pickup |
| PICKUP_CONFIRMATION | INSERT | Confirm collection | Collected by customer at 15:30 |
| HANDOVER_VERIFICATION | INSERT | Verify handover | ID verified, items checked |

#### 12.2 Notifications

**Description**: Send sale confirmations

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| EMAIL_QUEUE | INSERT | Email notifications | Invoice emailed to customer |
| SMS_QUEUE | INSERT | SMS confirmation | "Thank you for your purchase" |
| WHATSAPP_QUEUE | INSERT | WhatsApp message | Invoice shared on WhatsApp |

---

## 13. Analytics and Reporting

### Description

Update various analytical systems with sale data.

### Process Steps and Database Operations

#### 13.1 Sales Analytics

**Description**: Update sales performance metrics

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| DAILY_SALES_SUMMARY | UPDATE | Daily metrics | Jan 20: ₹5,25,000 total sales |
| PRODUCT_SALES_METRICS | UPDATE | Product performance | HP: 25 units sold MTD |
| CATEGORY_PERFORMANCE | UPDATE | Category metrics | Laptops: ₹15,00,000 MTD |
| SALESPERSON_PERFORMANCE | UPDATE | Individual metrics | User 102: ₹8,50,000 MTD |

#### 13.2 Inventory Analytics

**Description**: Update inventory metrics

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| INVENTORY_TURNOVER | UPDATE | Turnover rates | HP turnover: 3.5x |
| FAST_MOVING_ITEMS | UPDATE | Velocity tracking | HP in top 10 fast movers |
| STOCK_VALUATION | UPDATE | Inventory value | Total value decreased |

---

## 14. Compliance and Audit

### Description

Ensure all regulatory requirements are met.

### Process Steps and Database Operations

#### 14.1 Tax Compliance

**Description**: Update tax registers

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| GST_SALES_REGISTER | INSERT | GST compliance | IGST collected: ₹26,505 |
| E_INVOICE_GENERATION | INSERT | E-invoice if required | IRN generated |
| TAX_RETURN_DATA | UPDATE | Monthly tax data | January GST data updated |

#### 14.2 Audit Trail

**Description**: Complete audit logging

**Tables Affected:**

| Table | Operation | Purpose | Example |
|-------|-----------|---------|----------|
| AUDIT_LOG | INSERT | Comprehensive trail | 45 entries for this transaction |
| TRANSACTION_AUDIT | INSERT | Transaction-specific | Complete sale lifecycle logged |
| USER_ACTION_LOG | INSERT | User activities | All user 102 actions logged |

---

## Summary Statistics

### Transaction Volume Example

For a sale of 2 laptops + 3 monitors:

**Total Database Operations:**

- READ Operations: ~40
- INSERT Operations: ~65
- UPDATE Operations: ~30
- DELETE Operations: ~2

**Key Tables by Operation Count:**

1. **INVENTORY_UNIT**: 5 updates (status changes)
2. **TRANSACTION Tables**: 8+ inserts (header, lines, details)
3. **PAYMENT Tables**: 4+ inserts (payment, verification)
4. **STOCK_LEVEL**: 2 updates (per SKU)
5. **CUSTOMER Tables**: 5+ updates (history, loyalty)
6. **FINANCIAL Tables**: 6+ inserts (revenue, commission)
7. **DOCUMENT Tables**: 5+ inserts (invoice, delivery note)

### Performance Metrics

- Simple Sale (1-3 items): 3-5 minutes
- Medium Sale (5-10 items): 7-10 minutes
- Large Sale (20+ items): 15-20 minutes

### Critical Success Factors

1. **Inventory Accuracy**: Real-time availability prevents overselling
2. **Pricing Integrity**: Correct prices and discount application
3. **Payment Security**: Proper payment verification and recording
4. **Document Compliance**: GST-compliant invoicing
5. **Customer Satisfaction**: Quick processing and accurate documentation
6. **Stock Synchronization**: Multi-channel inventory updates
7. **Financial Accuracy**: Proper revenue and commission calculation

This comprehensive documentation demonstrates how a sales transaction orchestrates updates across inventory, financial, customer, and analytical systems while maintaining compliance and providing excellent customer service throughout the sales process.
