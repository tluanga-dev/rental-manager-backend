"""remove_purchase_transaction_status_column

Revision ID: f48aefefbd53
Revises: d221f0daa3fc
Create Date: 2025-06-30 23:15:05.534382

"""
from alembic import op
import sqlalchemy as sa


revision = 'f48aefefbd53'
down_revision = 'd221f0daa3fc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the status column from purchase_transactions table
    op.drop_column('purchase_transactions', 'status')
    
    # Drop the status index
    op.drop_index('ix_purchase_transactions_status', table_name='purchase_transactions')


def downgrade() -> None:
    # Add back the status column with default value
    op.add_column('purchase_transactions', 
                  sa.Column('status', 
                           sa.Enum('DRAFT', 'CONFIRMED', 'PROCESSING', 'RECEIVED', 'COMPLETED', 'CANCELLED', 
                                  name='purchasestatus'), 
                           nullable=False, 
                           server_default='DRAFT'))
    
    # Recreate the status index
    op.create_index('ix_purchase_transactions_status', 'purchase_transactions', ['status'])