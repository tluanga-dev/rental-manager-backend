from sqlalchemy import Column, String, Text, Index, ForeignKey, UniqueConstraint, Integer, Boolean, Enum, DECIMAL, CheckConstraint, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .base_model import TimeStampedModel


class ContactNumberModel(TimeStampedModel):
    __tablename__ = "contact_numbers"

    number = Column(String(20), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(String(36), nullable=True, index=True)

    __table_args__ = (
        Index('ix_contact_numbers_entity', 'entity_type', 'entity_id'),
        Index('ix_contact_numbers_unique', 'entity_type', 'entity_id', 'number', unique=True),
    )


class CustomerModel(TimeStampedModel):
    __tablename__ = "customers"

    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    address = Column(Text, nullable=True)
    remarks = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True, index=True)
    
    # Keep backward compatibility with old address fields
    street = Column(String(500), nullable=True)
    state = Column(String(50), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True, default="USA")


class VendorModel(TimeStampedModel):
    __tablename__ = "vendors"

    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    address = Column(Text, nullable=True)
    remarks = Column(String(255), nullable=True)
    city = Column(String(255), nullable=True, index=True)


class ItemPackagingModel(TimeStampedModel):
    __tablename__ = "item_packaging"

    name = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False, unique=True, index=True)
    unit = Column(String(255), nullable=False)
    remarks = Column(Text, nullable=True)

    __table_args__ = (
        Index('packaging_label_idx', 'label'),
    )


class UnitOfMeasurementModel(TimeStampedModel):
    __tablename__ = "unit_of_measurement"

    name = Column(String(255), nullable=False, unique=True, index=True)
    abbreviation = Column(String(8), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    __table_args__ = (
        Index('uom_abbreviation_idx', 'abbreviation'),
    )


class WarehouseModel(TimeStampedModel):
    __tablename__ = "warehouses"

    name = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False, unique=True, index=True)
    remarks = Column(Text, nullable=True)

    __table_args__ = (
        Index('warehouse_label_idx', 'label'),
    )


class ItemCategoryModel(TimeStampedModel):
    __tablename__ = "item_categories"

    name = Column(String(255), nullable=False, unique=True, index=True)
    abbreviation = Column(String(9), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Relationship to subcategories
    subcategories = relationship("ItemSubCategoryModel", back_populates="item_category", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_item_categories_name', 'name'),
        Index('ix_item_categories_abbreviation', 'abbreviation'),
    )


class ItemSubCategoryModel(TimeStampedModel):
    __tablename__ = "item_subcategories"

    name = Column(String(255), nullable=False, index=True)
    abbreviation = Column(String(9), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    item_category_id = Column(String(36), ForeignKey("item_categories.id"), nullable=False)

    # Relationship to parent category
    item_category = relationship("ItemCategoryModel", back_populates="subcategories")

    __table_args__ = (
        UniqueConstraint('name', 'item_category_id', name='unique_subcategory_name_per_category'),
        Index('ix_item_subcategories_name', 'name'),
        Index('ix_item_subcategories_abbreviation', 'abbreviation'),
        Index('ix_item_subcategories_category', 'item_category_id'),
    )


class IdManagerModel(TimeStampedModel):
    __tablename__ = "id_managers"

    prefix = Column(String(255), nullable=False, unique=True, index=True)
    latest_id = Column(Text, nullable=False)

    __table_args__ = (
        Index('id_manager_prefix_idx', 'prefix'),
    )


# Inventory Enums
class TrackingType(str, enum.Enum):
    BULK = "BULK"
    INDIVIDUAL = "INDIVIDUAL"


class InventoryItemStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    SOLD = "SOLD"
    MAINTENANCE = "MAINTENANCE"
    RETIRED = "RETIRED"
    LOST = "LOST"


class WarrantyPeriodType(str, enum.Enum):
    DAYS = "DAYS"
    MONTHS = "MONTHS"
    YEARS = "YEARS"


class MovementType(str, enum.Enum):
    PURCHASE = "PURCHASE"
    PURCHASE_RETURN = "PURCHASE_RETURN"
    SELL = "SELL"
    SELL_RETURN = "SELL_RETURN"
    RENT = "RENT"
    RENT_RETURN = "RENT_RETURN"
    RECONCILIATION = "RECONCILIATION"
    INTER_WAREHOUSE_TRANSFER = "INTER_WAREHOUSE_TRANSFER"


class InventoryItemMasterModel(TimeStampedModel):
    __tablename__ = "inventory_item_masters"

    name = Column(String(255), nullable=False, unique=True, index=True)
    sku = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    contents = Column(Text, nullable=True)
    item_sub_category_id = Column(String(36), ForeignKey("item_subcategories.id"), nullable=False)
    unit_of_measurement_id = Column(String(36), ForeignKey("unit_of_measurement.id"), nullable=False)
    packaging_id = Column(String(36), ForeignKey("item_packaging.id"), nullable=True)
    tracking_type = Column(Enum(TrackingType), nullable=False)
    is_consumable = Column(Boolean, default=False, nullable=False)
    brand = Column(String(255), nullable=True)
    manufacturer_part_number = Column(String(255), nullable=True)
    product_id = Column(String(255), nullable=True)
    weight = Column(DECIMAL(10, 3), nullable=True)
    length = Column(DECIMAL(10, 2), nullable=True)
    width = Column(DECIMAL(10, 2), nullable=True)
    height = Column(DECIMAL(10, 2), nullable=True)
    renting_period = Column(Integer, default=1, nullable=False)
    quantity = Column(Integer, default=0, nullable=False)

    # Relationships
    subcategory = relationship("ItemSubCategoryModel", backref="inventory_items")
    unit_of_measurement = relationship("UnitOfMeasurementModel", backref="inventory_items")
    packaging = relationship("ItemPackagingModel", backref="inventory_items")
    line_items = relationship("LineItemModel", back_populates="inventory_item_master", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('weight >= 0', name='check_positive_weight'),
        CheckConstraint('length >= 0', name='check_positive_length'),
        CheckConstraint('width >= 0', name='check_positive_width'),
        CheckConstraint('height >= 0', name='check_positive_height'),
        CheckConstraint('renting_period >= 1', name='check_min_renting_period'),
        Index('ix_inventory_item_masters_tracking_type', 'tracking_type'),
        Index('ix_inventory_item_masters_is_consumable', 'is_consumable'),
        Index('ix_inventory_item_masters_quantity', 'quantity'),
    )


class LineItemModel(TimeStampedModel):
    __tablename__ = "line_items"

    inventory_item_master_id = Column(String(36), ForeignKey("inventory_item_masters.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("warehouses.id"), nullable=False)
    status = Column(Enum(InventoryItemStatus), default=InventoryItemStatus.AVAILABLE, nullable=False)
    serial_number = Column(String(255), nullable=True, unique=True, index=True)
    quantity = Column(Integer, default=1, nullable=False)
    rental_rate = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    replacement_cost = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    late_fee_rate = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    sell_tax_rate = Column(Integer, default=0, nullable=False)
    rent_tax_rate = Column(Integer, default=0, nullable=False)
    rentable = Column(Boolean, default=True, nullable=False)
    sellable = Column(Boolean, default=False, nullable=False)
    selling_price = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    warranty_period_type = Column(Enum(WarrantyPeriodType), nullable=True)
    warranty_period = Column(Integer, nullable=True)

    # Relationships
    inventory_item_master = relationship("InventoryItemMasterModel", back_populates="line_items")
    warehouse = relationship("WarehouseModel", backref="line_items")
    movements = relationship("InventoryItemStockMovementModel", back_populates="inventory_item", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_non_negative_quantity'),
        UniqueConstraint('serial_number', name='unique_serial_number'),
        Index('ix_line_items_status', 'status'),
        Index('ix_line_items_rentable_sellable', 'rentable', 'sellable'),
    )


class InventoryItemStockMovementModel(TimeStampedModel):
    __tablename__ = "inventory_item_stock_movements"

    inventory_item_id = Column(String(36), ForeignKey("line_items.id"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    inventory_transaction_id = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    quantity_on_hand_before = Column(Integer, nullable=False)
    quantity_on_hand_after = Column(Integer, nullable=False)
    warehouse_from_id = Column(String(36), ForeignKey("warehouses.id"), nullable=True)
    warehouse_to_id = Column(String(36), ForeignKey("warehouses.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    inventory_item = relationship("LineItemModel", back_populates="movements")
    warehouse_from = relationship("WarehouseModel", foreign_keys=[warehouse_from_id], backref="outgoing_transfers")
    warehouse_to = relationship("WarehouseModel", foreign_keys=[warehouse_to_id], backref="incoming_transfers")

    __table_args__ = (
        Index('ix_inventory_movements_type', 'movement_type'),
        Index('ix_inventory_movements_created_at', 'created_at'),
    )



class PurchaseOrderModel(TimeStampedModel):
    __tablename__ = "purchase_orders"

    order_number = Column(String(50), nullable=False, unique=True, index=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=True)
    total_amount = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    total_tax_amount = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    total_discount = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    grand_total = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    reference_number = Column(String(255), nullable=True, index=True)
    invoice_number = Column(String(255), nullable=True, index=True)
    notes = Column(Text, nullable=True)

    # Relationships
    vendor = relationship("VendorModel", backref="purchase_orders")
    line_items = relationship("PurchaseOrderLineItemModel", back_populates="purchase_order", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_positive_total_amount'),
        CheckConstraint('total_tax_amount >= 0', name='check_positive_total_tax'),
        CheckConstraint('total_discount >= 0', name='check_positive_total_discount'),
        CheckConstraint('grand_total >= 0', name='check_positive_grand_total'),
        Index('ix_purchase_orders_order_date', 'order_date'),
        Index('ix_purchase_orders_vendor', 'vendor_id'),
    )


class PurchaseOrderLineItemModel(TimeStampedModel):
    __tablename__ = "purchase_order_line_items"

    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    inventory_item_master_id = Column(String(36), ForeignKey("inventory_item_masters.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(12, 2), nullable=False)
    serial_number = Column(String(255), nullable=True, index=True)
    discount = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    tax_amount = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    received_quantity = Column(Integer, default=0, nullable=False)
    reference_number = Column(String(255), nullable=True)
    warranty_period_type = Column(Enum(WarrantyPeriodType), nullable=True)
    warranty_period = Column(Integer, nullable=True)


    # Relationships
    purchase_order = relationship("PurchaseOrderModel", back_populates="line_items")
    inventory_item_master = relationship("InventoryItemMasterModel", backref="purchase_order_line_items")
    warehouse = relationship("WarehouseModel", backref="purchase_order_line_items")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        CheckConstraint('unit_price >= 0', name='check_non_negative_unit_price'),
        CheckConstraint('discount >= 0', name='check_non_negative_discount'),
        CheckConstraint('tax_amount >= 0', name='check_non_negative_tax'),
        Index('ix_purchase_order_line_items_serial', 'serial_number'),
        Index('ix_purchase_order_line_items_inventory', 'inventory_item_master_id'),
        Index('ix_purchase_order_line_items_warehouse', 'warehouse_id'),
    )


# Sales Enums
class SalesStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    REFUNDED = "REFUNDED"


class PaymentTerms(str, enum.Enum):
    IMMEDIATE = "IMMEDIATE"
    NET_15 = "NET_15"
    NET_30 = "NET_30"
    NET_45 = "NET_45"
    NET_60 = "NET_60"
    NET_90 = "NET_90"
    COD = "COD"
    PREPAID = "PREPAID"


class SalesTransactionModel(TimeStampedModel):
    __tablename__ = "sales_transactions"

    transaction_id = Column(String(20), nullable=False, unique=True, index=True)
    invoice_number = Column(String(50), nullable=True, unique=True, index=True)
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    delivery_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(SalesStatus), default=SalesStatus.DRAFT, nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_terms = Column(Enum(PaymentTerms), default=PaymentTerms.IMMEDIATE, nullable=False)
    payment_due_date = Column(Date, nullable=True)
    subtotal = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    shipping_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    grand_total = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    amount_paid = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    shipping_address = Column(Text, nullable=True)
    billing_address = Column(Text, nullable=True)
    purchase_order_number = Column(String(50), nullable=True)
    # TODO: Add foreign key to user table when authentication is implemented
    sales_person_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)
    customer_notes = Column(Text, nullable=True)

    # Relationships
    customer = relationship("CustomerModel", backref="sales_transactions")
    items = relationship("SalesTransactionItemModel", back_populates="transaction", cascade="all, delete-orphan")
    returns = relationship("SalesReturnModel", back_populates="sales_transaction", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('subtotal >= 0', name='check_positive_subtotal'),
        CheckConstraint('discount_amount >= 0', name='check_positive_discount'),
        CheckConstraint('tax_amount >= 0', name='check_positive_tax'),
        CheckConstraint('shipping_amount >= 0', name='check_positive_shipping'),
        CheckConstraint('grand_total >= 0', name='check_positive_grand_total'),
        CheckConstraint('amount_paid >= 0', name='check_positive_amount_paid'),
        Index('ix_sales_transactions_status', 'status'),
        Index('ix_sales_transactions_payment_status', 'payment_status'),
        Index('ix_sales_transactions_order_date', 'order_date'),
        Index('ix_sales_transactions_customer', 'customer_id'),
        Index('ix_sales_transactions_sales_person', 'sales_person_id'),
    )


class SalesTransactionItemModel(TimeStampedModel):
    __tablename__ = "sales_transaction_items"

    transaction_id = Column(String(36), ForeignKey("sales_transactions.id"), nullable=False)
    inventory_item_master_id = Column(String(36), ForeignKey("inventory_item_masters.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    cost_price = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), default=0.0, nullable=False)
    discount_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    tax_rate = Column(DECIMAL(5, 2), default=0.0, nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    subtotal = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    total = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    serial_numbers = Column(JSON, default=list, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    transaction = relationship("SalesTransactionModel", back_populates="items")
    inventory_item_master = relationship("InventoryItemMasterModel", backref="sales_items")
    warehouse = relationship("WarehouseModel", backref="sales_items")
    return_items = relationship("SalesReturnItemModel", back_populates="sales_item", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_sales_quantity'),
        CheckConstraint('unit_price >= 0', name='check_non_negative_unit_price'),
        CheckConstraint('cost_price >= 0', name='check_non_negative_cost_price'),
        CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='check_discount_percentage_range'),
        CheckConstraint('discount_amount >= 0', name='check_non_negative_discount_amount'),
        CheckConstraint('tax_rate >= 0 AND tax_rate <= 100', name='check_tax_rate_range'),
        CheckConstraint('tax_amount >= 0', name='check_non_negative_tax_amount'),
        Index('ix_sales_transaction_items_transaction', 'transaction_id'),
        Index('ix_sales_transaction_items_inventory', 'inventory_item_master_id'),
        Index('ix_sales_transaction_items_warehouse', 'warehouse_id'),
    )


class SalesReturnModel(TimeStampedModel):
    __tablename__ = "sales_returns"

    return_id = Column(String(20), nullable=False, unique=True, index=True)
    sales_transaction_id = Column(String(36), ForeignKey("sales_transactions.id"), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    reason = Column(Text, nullable=False)
    # TODO: Add foreign key to user table when authentication is implemented
    approved_by_id = Column(String(36), nullable=True)
    refund_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    restocking_fee = Column(DECIMAL(10, 2), default=0.0, nullable=False)

    # Relationships
    sales_transaction = relationship("SalesTransactionModel", back_populates="returns")
    items = relationship("SalesReturnItemModel", back_populates="sales_return", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('refund_amount >= 0', name='check_positive_refund_amount'),
        CheckConstraint('restocking_fee >= 0', name='check_positive_restocking_fee'),
        Index('ix_sales_returns_transaction', 'sales_transaction_id'),
        Index('ix_sales_returns_return_date', 'return_date'),
        Index('ix_sales_returns_approved_by', 'approved_by_id'),
    )


class SalesReturnItemModel(TimeStampedModel):
    __tablename__ = "sales_return_items"

    sales_return_id = Column(String(36), ForeignKey("sales_returns.id"), nullable=False)
    sales_item_id = Column(String(36), ForeignKey("sales_transaction_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    condition = Column(String(50), nullable=False)
    serial_numbers = Column(JSON, default=list, nullable=False)

    # Relationships
    sales_return = relationship("SalesReturnModel", back_populates="items")
    sales_item = relationship("SalesTransactionItemModel", back_populates="return_items")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_return_quantity'),
        Index('ix_sales_return_items_return', 'sales_return_id'),
        Index('ix_sales_return_items_sales_item', 'sales_item_id'),
    )


# WarrantyPeriodType enum already exists, so we just reference it in string form


class PurchaseTransactionModel(TimeStampedModel):
    __tablename__ = "purchase_transactions"

    transaction_id = Column(String(255), nullable=False, unique=True, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    vendor_id = Column(String(36), ForeignKey("vendors.id"), nullable=False)
    total_amount = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    grand_total = Column(DECIMAL(12, 2), default=0.0, nullable=False)
    purchase_order_number = Column(String(255), nullable=True, index=True)
    remarks = Column(Text, nullable=True)

    # Relationships
    vendor = relationship("VendorModel", backref="purchase_transactions")
    items = relationship("PurchaseTransactionItemModel", back_populates="transaction", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='check_positive_total_amount'),
        CheckConstraint('grand_total >= 0', name='check_positive_grand_total'),
        Index('ix_purchase_transactions_vendor', 'vendor_id'),
        Index('ix_purchase_transactions_date', 'transaction_date'),
        Index('ix_purchase_transactions_po_number', 'purchase_order_number'),
    )


class PurchaseTransactionItemModel(TimeStampedModel):
    __tablename__ = "purchase_transaction_items"

    transaction_id = Column(String(36), ForeignKey("purchase_transactions.id"), nullable=False)
    inventory_item_id = Column(String(36), ForeignKey("inventory_item_masters.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("warehouses.id"), nullable=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    discount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    tax_amount = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    total_price = Column(DECIMAL(10, 2), default=0.0, nullable=False)
    serial_number = Column(JSON, default=list, nullable=False)
    remarks = Column(Text, nullable=True)
    warranty_period_type = Column(Enum('DAYS', 'MONTHS', 'YEARS', name='warrantyperiodtype'), nullable=True)
    warranty_period = Column(Integer, nullable=True)

    # Relationships
    transaction = relationship("PurchaseTransactionModel", back_populates="items")
    inventory_item = relationship("InventoryItemMasterModel", backref="purchase_items")
    warehouse = relationship("WarehouseModel", backref="purchase_items")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_purchase_quantity'),
        CheckConstraint('unit_price >= 0', name='check_non_negative_unit_price'),
        CheckConstraint('discount >= 0', name='check_non_negative_discount'),
        CheckConstraint('tax_amount >= 0', name='check_non_negative_tax_amount'),
        CheckConstraint('total_price >= 0', name='check_non_negative_total_price'),
        CheckConstraint('warranty_period IS NULL OR warranty_period > 0', name='check_positive_warranty_period'),
        CheckConstraint(
            '(warranty_period_type IS NULL AND warranty_period IS NULL) OR '
            '(warranty_period_type IS NOT NULL AND warranty_period IS NOT NULL)',
            name='check_warranty_consistency'
        ),
        Index('ix_purchase_transaction_items_transaction', 'transaction_id'),
        Index('ix_purchase_transaction_items_inventory', 'inventory_item_id'),
        Index('ix_purchase_transaction_items_warehouse', 'warehouse_id'),
    )