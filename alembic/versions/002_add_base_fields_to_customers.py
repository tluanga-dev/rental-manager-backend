"""add base fields to customers

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('customers', sa.Column('created_by', sa.String(length=255), nullable=True))
    op.add_column('customers', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('customers', 'is_active')
    op.drop_column('customers', 'created_by')