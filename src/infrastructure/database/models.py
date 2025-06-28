from sqlalchemy import Column, String, Text, Index, ForeignKey, UniqueConstraint, Integer, Boolean, Enum, DECIMAL, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from .base_model import TimeStampedModel


class ContactNumberModel(TimeStampedModel):
    __tablename__ = "contact_numbers"

    number = Column(String(20), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)

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
    item_category_id = Column(UUID(as_uuid=True), ForeignKey("item_categories.id"), nullable=False)

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
    item_sub_category_id = Column(UUID(as_uuid=True), ForeignKey("item_subcategories.id"), nullable=False)
    unit_of_measurement_id = Column(UUID(as_uuid=True), ForeignKey("unit_of_measurements.id"), nullable=False)
    packaging_id = Column(UUID(as_uuid=True), ForeignKey("item_packaging.id"), nullable=True)
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

    inventory_item_master_id = Column(UUID(as_uuid=True), ForeignKey("inventory_item_masters.id"), nullable=False)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=False)
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

    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("line_items.id"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    inventory_transaction_id = Column(String(255), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    quantity_on_hand_before = Column(Integer, nullable=False)
    quantity_on_hand_after = Column(Integer, nullable=False)
    warehouse_from_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    warehouse_to_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    inventory_item = relationship("LineItemModel", back_populates="movements")
    warehouse_from = relationship("WarehouseModel", foreign_keys=[warehouse_from_id], backref="outgoing_transfers")
    warehouse_to = relationship("WarehouseModel", foreign_keys=[warehouse_to_id], backref="incoming_transfers")

    __table_args__ = (
        Index('ix_inventory_movements_type', 'movement_type'),
        Index('ix_inventory_movements_created_at', 'created_at'),
    )