"""Add sales module tables

Revision ID: 1bf5fc286e10
Revises: c5d814f88329
Create Date: 2025-06-30 06:49:22.045735

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '1bf5fc286e10'
down_revision = 'c5d814f88329'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create sales enums if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE salesstatus AS ENUM ('DRAFT', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE paymentstatus AS ENUM ('PENDING', 'PARTIAL', 'PAID', 'OVERDUE', 'REFUNDED');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE paymentterms AS ENUM ('IMMEDIATE', 'NET_15', 'NET_30', 'NET_45', 'NET_60', 'NET_90', 'COD', 'PREPAID');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create sales_transactions table
    op.create_table('sales_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', sa.String(length=20), nullable=False),
        sa.Column('invoice_number', sa.String(length=50), nullable=True),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('delivery_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', postgresql.ENUM('DRAFT', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', name='salesstatus', create_type=False), nullable=False),
        sa.Column('payment_status', postgresql.ENUM('PENDING', 'PARTIAL', 'PAID', 'OVERDUE', 'REFUNDED', name='paymentstatus', create_type=False), nullable=False),
        sa.Column('payment_terms', postgresql.ENUM('IMMEDIATE', 'NET_15', 'NET_30', 'NET_45', 'NET_60', 'NET_90', 'COD', 'PREPAID', name='paymentterms', create_type=False), nullable=False),
        sa.Column('payment_due_date', sa.Date(), nullable=True),
        sa.Column('subtotal', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('discount_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('tax_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('shipping_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('grand_total', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('amount_paid', sa.DECIMAL(precision=12, scale=2), nullable=False),
        sa.Column('shipping_address', sa.Text(), nullable=True),
        sa.Column('billing_address', sa.Text(), nullable=True),
        sa.Column('purchase_order_number', sa.String(length=50), nullable=True),
        sa.Column('sales_person_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('customer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.CheckConstraint('amount_paid >= 0', name='check_positive_amount_paid'),
        sa.CheckConstraint('discount_amount >= 0', name='check_positive_discount'),
        sa.CheckConstraint('grand_total >= 0', name='check_positive_grand_total'),
        sa.CheckConstraint('shipping_amount >= 0', name='check_positive_shipping'),
        sa.CheckConstraint('subtotal >= 0', name='check_positive_subtotal'),
        sa.CheckConstraint('tax_amount >= 0', name='check_positive_tax'),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number'),
        sa.UniqueConstraint('transaction_id')
    )
    op.create_index(op.f('ix_sales_transactions_customer'), 'sales_transactions', ['customer_id'], unique=False)
    op.create_index(op.f('ix_sales_transactions_invoice_number'), 'sales_transactions', ['invoice_number'], unique=False)
    op.create_index(op.f('ix_sales_transactions_order_date'), 'sales_transactions', ['order_date'], unique=False)
    op.create_index(op.f('ix_sales_transactions_payment_status'), 'sales_transactions', ['payment_status'], unique=False)
    op.create_index(op.f('ix_sales_transactions_sales_person'), 'sales_transactions', ['sales_person_id'], unique=False)
    op.create_index(op.f('ix_sales_transactions_status'), 'sales_transactions', ['status'], unique=False)
    op.create_index(op.f('ix_sales_transactions_transaction_id'), 'sales_transactions', ['transaction_id'], unique=False)
    
    # Create sales_transaction_items table
    op.create_table('sales_transaction_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('inventory_item_master_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('cost_price', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('discount_percentage', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('discount_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('tax_rate', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('tax_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('subtotal', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('serial_numbers', sa.JSON(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.CheckConstraint('cost_price >= 0', name='check_non_negative_cost_price'),
        sa.CheckConstraint('discount_amount >= 0', name='check_non_negative_discount_amount'),
        sa.CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='check_discount_percentage_range'),
        sa.CheckConstraint('quantity > 0', name='check_positive_sales_quantity'),
        sa.CheckConstraint('tax_amount >= 0', name='check_non_negative_tax_amount'),
        sa.CheckConstraint('tax_rate >= 0 AND tax_rate <= 100', name='check_tax_rate_range'),
        sa.CheckConstraint('unit_price >= 0', name='check_non_negative_unit_price'),
        sa.ForeignKeyConstraint(['inventory_item_master_id'], ['inventory_item_masters.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['sales_transactions.id'], ),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_transaction_items_inventory'), 'sales_transaction_items', ['inventory_item_master_id'], unique=False)
    op.create_index(op.f('ix_sales_transaction_items_transaction'), 'sales_transaction_items', ['transaction_id'], unique=False)
    op.create_index(op.f('ix_sales_transaction_items_warehouse'), 'sales_transaction_items', ['warehouse_id'], unique=False)
    
    # Create sales_returns table
    op.create_table('sales_returns',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('return_id', sa.String(length=20), nullable=False),
        sa.Column('sales_transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('return_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('approved_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('refund_amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('restocking_fee', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.CheckConstraint('refund_amount >= 0', name='check_positive_refund_amount'),
        sa.CheckConstraint('restocking_fee >= 0', name='check_positive_restocking_fee'),
        sa.ForeignKeyConstraint(['sales_transaction_id'], ['sales_transactions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('return_id')
    )
    op.create_index(op.f('ix_sales_returns_approved_by'), 'sales_returns', ['approved_by_id'], unique=False)
    op.create_index(op.f('ix_sales_returns_return_date'), 'sales_returns', ['return_date'], unique=False)
    op.create_index(op.f('ix_sales_returns_return_id'), 'sales_returns', ['return_id'], unique=False)
    op.create_index(op.f('ix_sales_returns_transaction'), 'sales_returns', ['sales_transaction_id'], unique=False)
    
    # Create sales_return_items table
    op.create_table('sales_return_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_return_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sales_item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('condition', sa.String(length=50), nullable=False),
        sa.Column('serial_numbers', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.CheckConstraint('quantity > 0', name='check_positive_return_quantity'),
        sa.ForeignKeyConstraint(['sales_item_id'], ['sales_transaction_items.id'], ),
        sa.ForeignKeyConstraint(['sales_return_id'], ['sales_returns.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_return_items_return'), 'sales_return_items', ['sales_return_id'], unique=False)
    op.create_index(op.f('ix_sales_return_items_sales_item'), 'sales_return_items', ['sales_item_id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_sales_return_items_sales_item'), table_name='sales_return_items')
    op.drop_index(op.f('ix_sales_return_items_return'), table_name='sales_return_items')
    op.drop_table('sales_return_items')
    op.drop_index(op.f('ix_sales_returns_transaction'), table_name='sales_returns')
    op.drop_index(op.f('ix_sales_returns_return_id'), table_name='sales_returns')
    op.drop_index(op.f('ix_sales_returns_return_date'), table_name='sales_returns')
    op.drop_index(op.f('ix_sales_returns_approved_by'), table_name='sales_returns')
    op.drop_table('sales_returns')
    op.drop_index(op.f('ix_sales_transaction_items_warehouse'), table_name='sales_transaction_items')
    op.drop_index(op.f('ix_sales_transaction_items_transaction'), table_name='sales_transaction_items')
    op.drop_index(op.f('ix_sales_transaction_items_inventory'), table_name='sales_transaction_items')
    op.drop_table('sales_transaction_items')
    op.drop_index(op.f('ix_sales_transactions_transaction_id'), table_name='sales_transactions')
    op.drop_index(op.f('ix_sales_transactions_status'), table_name='sales_transactions')
    op.drop_index(op.f('ix_sales_transactions_sales_person'), table_name='sales_transactions')
    op.drop_index(op.f('ix_sales_transactions_payment_status'), table_name='sales_transactions')
    op.drop_index(op.f('ix_sales_transactions_order_date'), table_name='sales_transactions')
    op.drop_index(op.f('ix_sales_transactions_invoice_number'), table_name='sales_transactions')
    op.drop_index(op.f('ix_sales_transactions_customer'), table_name='sales_transactions')
    op.drop_table('sales_transactions')
    
    # Drop enums if they exist
    op.execute("DROP TYPE IF EXISTS paymentterms")
    op.execute("DROP TYPE IF EXISTS paymentstatus")
    op.execute("DROP TYPE IF EXISTS salesstatus")