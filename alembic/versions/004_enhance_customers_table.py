"""enhance customers table with new fields

Revision ID: 004
Revises: 003
Create Date: 2024-01-01 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new fields to customers table
    op.add_column('customers', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('customers', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('customers', sa.Column('remarks', sa.String(length=255), nullable=True))
    
    # Rename existing city column (if it conflicts) and add the enhanced city column
    try:
        op.drop_column('customers', 'city')
    except:
        pass  # Column might not exist
    op.add_column('customers', sa.Column('city', sa.String(length=255), nullable=True))
    
    # Make existing address fields nullable for backward compatibility
    op.alter_column('customers', 'street', nullable=True)
    op.alter_column('customers', 'state', nullable=True)
    op.alter_column('customers', 'zip_code', nullable=True)
    op.alter_column('customers', 'country', nullable=True)
    
    # Add indexes for new fields
    op.create_index(op.f('ix_customers_email'), 'customers', ['email'], unique=True)
    op.create_index(op.f('ix_customers_city'), 'customers', ['city'], unique=False)


def downgrade() -> None:
    # Remove indexes
    op.drop_index(op.f('ix_customers_city'), table_name='customers')
    op.drop_index(op.f('ix_customers_email'), table_name='customers')
    
    # Remove new columns
    op.drop_column('customers', 'city')
    op.drop_column('customers', 'remarks')
    op.drop_column('customers', 'address')
    op.drop_column('customers', 'email')
    
    # Restore original column constraints
    op.alter_column('customers', 'street', nullable=False)
    op.alter_column('customers', 'state', nullable=False)
    op.alter_column('customers', 'zip_code', nullable=False)
    op.alter_column('customers', 'country', nullable=False)