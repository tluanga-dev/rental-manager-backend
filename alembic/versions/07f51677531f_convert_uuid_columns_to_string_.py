"""Convert UUID columns to string representation

Revision ID: 07f51677531f
Revises: f48aefefbd53
Create Date: 2025-07-01 06:40:33.799365

"""
from alembic import op
import sqlalchemy as sa


revision = '07f51677531f'
down_revision = 'f48aefefbd53'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No schema changes needed - UUID(as_uuid=False) already updated in models
    # This migration ensures existing data remains accessible
    # PostgreSQL will automatically handle UUID to string conversion
    pass


def downgrade() -> None:
    # Downgrade would require converting back to UUID(as_uuid=True)
    # This is not recommended as it would break the string UUID pattern
    pass