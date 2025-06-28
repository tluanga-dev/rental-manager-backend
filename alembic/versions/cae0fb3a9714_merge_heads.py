"""merge heads

Revision ID: cae0fb3a9714
Revises: 008, 009
Create Date: 2025-06-28 14:04:47.239490

"""
from alembic import op
import sqlalchemy as sa


revision = 'cae0fb3a9714'
down_revision = ('36168e2b083f', '009')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass