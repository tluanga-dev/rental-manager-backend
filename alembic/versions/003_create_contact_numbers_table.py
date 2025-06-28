"""create contact_numbers table

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('contact_numbers',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('number', sa.String(length=20), nullable=False),
    sa.Column('entity_type', sa.String(length=50), nullable=True),
    sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_by', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contact_numbers_id'), 'contact_numbers', ['id'], unique=False)
    op.create_index(op.f('ix_contact_numbers_number'), 'contact_numbers', ['number'], unique=False)
    op.create_index(op.f('ix_contact_numbers_entity_type'), 'contact_numbers', ['entity_type'], unique=False)
    op.create_index(op.f('ix_contact_numbers_entity_id'), 'contact_numbers', ['entity_id'], unique=False)
    op.create_index('ix_contact_numbers_entity', 'contact_numbers', ['entity_type', 'entity_id'], unique=False)
    op.create_index('ix_contact_numbers_unique', 'contact_numbers', ['entity_type', 'entity_id', 'number'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_contact_numbers_unique', table_name='contact_numbers')
    op.drop_index('ix_contact_numbers_entity', table_name='contact_numbers')
    op.drop_index(op.f('ix_contact_numbers_entity_id'), table_name='contact_numbers')
    op.drop_index(op.f('ix_contact_numbers_entity_type'), table_name='contact_numbers')
    op.drop_index(op.f('ix_contact_numbers_number'), table_name='contact_numbers')
    op.drop_index(op.f('ix_contact_numbers_id'), table_name='contact_numbers')
    op.drop_table('contact_numbers')