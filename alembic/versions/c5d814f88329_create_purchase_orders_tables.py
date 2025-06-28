"""Create purchase orders tables

Revision ID: c5d814f88329
Revises: cae0fb3a9714
Create Date: 2025-06-28 20:42:23.513062

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'c5d814f88329'
down_revision = 'cae0fb3a9714'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create purchase order status enum if it doesn't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE purchaseorderstatus AS ENUM ('DRAFT', 'ORDERED', 'PARTIAL_RECEIVED', 'RECEIVED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create purchase_orders table
    op.create_table('purchase_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('vendor_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('expected_delivery_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('DRAFT', 'ORDERED', 'PARTIAL_RECEIVED', 'RECEIVED', 'CANCELLED', name='purchaseorderstatus'), nullable=False, server_default='DRAFT'),
        sa.Column('total_amount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_tax_amount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('total_discount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('grand_total', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('reference_number', sa.String(length=255), nullable=True),
        sa.Column('invoice_number', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.CheckConstraint('total_amount >= 0', name='check_positive_total_amount'),
        sa.CheckConstraint('total_tax_amount >= 0', name='check_positive_total_tax'),
        sa.CheckConstraint('total_discount >= 0', name='check_positive_total_discount'),
        sa.CheckConstraint('grand_total >= 0', name='check_positive_grand_total'),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index(op.f('ix_purchase_orders_id'), 'purchase_orders', ['id'], unique=False)
    op.create_index('ix_purchase_orders_order_date', 'purchase_orders', ['order_date'], unique=False)
    op.create_index('ix_purchase_orders_order_number', 'purchase_orders', ['order_number'], unique=True)
    op.create_index('ix_purchase_orders_status', 'purchase_orders', ['status'], unique=False)
    op.create_index('ix_purchase_orders_vendor', 'purchase_orders', ['vendor_id'], unique=False)
    op.create_index('ix_purchase_orders_reference_number', 'purchase_orders', ['reference_number'], unique=False)
    op.create_index('ix_purchase_orders_invoice_number', 'purchase_orders', ['invoice_number'], unique=False)
    
    # Create purchase_order_line_items table
    op.create_table('purchase_order_line_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_item_master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('serial_number', sa.String(length=255), nullable=True),
        sa.Column('discount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('tax_amount', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('received_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reference_number', sa.String(length=255), nullable=True),
        sa.Column('warranty_period_type', sa.Enum('DAYS', 'MONTHS', 'YEARS', name='warrantyperiodtype'), nullable=True),
        sa.Column('warranty_period', sa.Integer(), nullable=True),
        sa.Column('rental_rate', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('replacement_cost', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.Column('late_fee_rate', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0'),
        sa.Column('sell_tax_rate', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rent_tax_rate', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rentable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sellable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('selling_price', sa.DECIMAL(precision=12, scale=2), nullable=False, server_default='0'),
        sa.CheckConstraint('quantity > 0', name='check_positive_quantity'),
        sa.CheckConstraint('unit_price >= 0', name='check_non_negative_unit_price'),
        sa.CheckConstraint('discount >= 0', name='check_non_negative_discount'),
        sa.CheckConstraint('tax_amount >= 0', name='check_non_negative_tax'),
        sa.CheckConstraint('received_quantity >= 0', name='check_non_negative_received_qty'),
        sa.CheckConstraint('sell_tax_rate >= 0 AND sell_tax_rate <= 100', name='check_sell_tax_rate_range'),
        sa.CheckConstraint('rent_tax_rate >= 0 AND rent_tax_rate <= 100', name='check_rent_tax_rate_range'),
        sa.ForeignKeyConstraint(['inventory_item_master_id'], ['inventory_item_masters.id'], ),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_order_line_items_id'), 'purchase_order_line_items', ['id'], unique=False)
    op.create_index('ix_purchase_order_line_items_inventory', 'purchase_order_line_items', ['inventory_item_master_id'], unique=False)
    op.create_index('ix_purchase_order_line_items_serial', 'purchase_order_line_items', ['serial_number'], unique=False)
    op.create_index('ix_purchase_order_line_items_warehouse', 'purchase_order_line_items', ['warehouse_id'], unique=False)


def downgrade() -> None:
    # Drop purchase_order_line_items table
    op.drop_index('ix_purchase_order_line_items_warehouse', table_name='purchase_order_line_items')
    op.drop_index('ix_purchase_order_line_items_serial', table_name='purchase_order_line_items')
    op.drop_index('ix_purchase_order_line_items_inventory', table_name='purchase_order_line_items')
    op.drop_index(op.f('ix_purchase_order_line_items_id'), table_name='purchase_order_line_items')
    op.drop_table('purchase_order_line_items')
    
    # Drop purchase_orders table
    op.drop_index('ix_purchase_orders_invoice_number', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_reference_number', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_vendor', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_status', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_order_number', table_name='purchase_orders')
    op.drop_index('ix_purchase_orders_order_date', table_name='purchase_orders')
    op.drop_index(op.f('ix_purchase_orders_id'), table_name='purchase_orders')
    op.drop_table('purchase_orders')
    
    # Drop enums
    op.execute("DROP TYPE purchaseorderstatus")