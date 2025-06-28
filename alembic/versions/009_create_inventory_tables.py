"""Create inventory tables

Revision ID: 009
Revises: 8e8ec3b7555d
Create Date: 2025-06-28 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '8e8ec3b7555d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create inventory_item_masters table
    op.create_table('inventory_item_masters',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sku', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contents', sa.Text(), nullable=True),
        sa.Column('item_sub_category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unit_of_measurement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('packaging_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tracking_type', sa.Enum('BULK', 'INDIVIDUAL', name='trackingtype'), nullable=False),
        sa.Column('is_consumable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('brand', sa.String(length=255), nullable=True),
        sa.Column('manufacturer_part_number', sa.String(length=255), nullable=True),
        sa.Column('product_id', sa.String(length=255), nullable=True),
        sa.Column('weight', sa.DECIMAL(precision=10, scale=3), nullable=True),
        sa.Column('length', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('width', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('height', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('renting_period', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['item_sub_category_id'], ['item_subcategories.id'], ),
        sa.ForeignKeyConstraint(['packaging_id'], ['item_packaging.id'], ),
        sa.ForeignKeyConstraint(['unit_of_measurement_id'], ['unit_of_measurement.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('sku'),
        sa.CheckConstraint('weight >= 0', name='check_positive_weight'),
        sa.CheckConstraint('length >= 0', name='check_positive_length'),
        sa.CheckConstraint('width >= 0', name='check_positive_width'),
        sa.CheckConstraint('height >= 0', name='check_positive_height'),
        sa.CheckConstraint('renting_period >= 1', name='check_min_renting_period')
    )
    op.create_index(op.f('ix_inventory_item_masters_id'), 'inventory_item_masters', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_item_masters_name'), 'inventory_item_masters', ['name'], unique=True)
    op.create_index(op.f('ix_inventory_item_masters_sku'), 'inventory_item_masters', ['sku'], unique=True)
    op.create_index('ix_inventory_item_masters_tracking_type', 'inventory_item_masters', ['tracking_type'], unique=False)
    op.create_index('ix_inventory_item_masters_is_consumable', 'inventory_item_masters', ['is_consumable'], unique=False)
    op.create_index('ix_inventory_item_masters_quantity', 'inventory_item_masters', ['quantity'], unique=False)

    # Create line_items table
    op.create_table('line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inventory_item_master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('AVAILABLE', 'RENTED', 'SOLD', 'MAINTENANCE', 'RETIRED', 'LOST', name='inventoryitemstatus'), nullable=False, server_default='AVAILABLE'),
        sa.Column('serial_number', sa.String(length=255), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('rental_rate', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.0'),
        sa.Column('replacement_cost', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.0'),
        sa.Column('late_fee_rate', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0.0'),
        sa.Column('sell_tax_rate', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rent_tax_rate', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rentable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sellable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('selling_price', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0.0'),
        sa.Column('warranty_period_type', sa.Enum('DAYS', 'MONTHS', 'YEARS', name='warrantyperiodtype'), nullable=True),
        sa.Column('warranty_period', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['inventory_item_master_id'], ['inventory_item_masters.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('serial_number', name='unique_serial_number'),
        sa.CheckConstraint('quantity >= 0', name='check_non_negative_quantity')
    )
    op.create_index(op.f('ix_line_items_id'), 'line_items', ['id'], unique=False)
    op.create_index(op.f('ix_line_items_serial_number'), 'line_items', ['serial_number'], unique=True)
    op.create_index('ix_line_items_status', 'line_items', ['status'], unique=False)
    op.create_index('ix_line_items_rentable_sellable', 'line_items', ['rentable', 'sellable'], unique=False)

    # Create inventory_item_stock_movements table
    op.create_table('inventory_item_stock_movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('inventory_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('movement_type', sa.Enum('PURCHASE', 'PURCHASE_RETURN', 'SELL', 'SELL_RETURN', 'RENT', 'RENT_RETURN', 'RECONCILIATION', 'INTER_WAREHOUSE_TRANSFER', name='movementtype'), nullable=False),
        sa.Column('inventory_transaction_id', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('quantity_on_hand_before', sa.Integer(), nullable=False),
        sa.Column('quantity_on_hand_after', sa.Integer(), nullable=False),
        sa.Column('warehouse_from_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('warehouse_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['line_items.id'], ),
        sa.ForeignKeyConstraint(['warehouse_from_id'], ['warehouses.id'], ),
        sa.ForeignKeyConstraint(['warehouse_to_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_item_stock_movements_id'), 'inventory_item_stock_movements', ['id'], unique=False)
    op.create_index(op.f('ix_inventory_item_stock_movements_inventory_transaction_id'), 'inventory_item_stock_movements', ['inventory_transaction_id'], unique=False)
    op.create_index('ix_inventory_movements_type', 'inventory_item_stock_movements', ['movement_type'], unique=False)
    op.create_index('ix_inventory_movements_created_at', 'inventory_item_stock_movements', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop inventory_item_stock_movements table
    op.drop_index('ix_inventory_movements_created_at', table_name='inventory_item_stock_movements')
    op.drop_index('ix_inventory_movements_type', table_name='inventory_item_stock_movements')
    op.drop_index(op.f('ix_inventory_item_stock_movements_inventory_transaction_id'), table_name='inventory_item_stock_movements')
    op.drop_index(op.f('ix_inventory_item_stock_movements_id'), table_name='inventory_item_stock_movements')
    op.drop_table('inventory_item_stock_movements')
    
    # Drop line_items table
    op.drop_index('ix_line_items_rentable_sellable', table_name='line_items')
    op.drop_index('ix_line_items_status', table_name='line_items')
    op.drop_index(op.f('ix_line_items_serial_number'), table_name='line_items')
    op.drop_index(op.f('ix_line_items_id'), table_name='line_items')
    op.drop_table('line_items')
    
    # Drop inventory_item_masters table
    op.drop_index('ix_inventory_item_masters_quantity', table_name='inventory_item_masters')
    op.drop_index('ix_inventory_item_masters_is_consumable', table_name='inventory_item_masters')
    op.drop_index('ix_inventory_item_masters_tracking_type', table_name='inventory_item_masters')
    op.drop_index(op.f('ix_inventory_item_masters_sku'), table_name='inventory_item_masters')
    op.drop_index(op.f('ix_inventory_item_masters_name'), table_name='inventory_item_masters')
    op.drop_index(op.f('ix_inventory_item_masters_id'), table_name='inventory_item_masters')
    op.drop_table('inventory_item_masters')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS movementtype')
    op.execute('DROP TYPE IF EXISTS warrantyperiodtype')
    op.execute('DROP TYPE IF EXISTS inventoryitemstatus')
    op.execute('DROP TYPE IF EXISTS trackingtype')