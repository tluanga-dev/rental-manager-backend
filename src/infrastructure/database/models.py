from sqlalchemy import Column, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID

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


class ItemPackagingModel(TimeStampedModel):
    __tablename__ = "item_packaging"

    name = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False, unique=True, index=True)
    unit = Column(String(255), nullable=False)
    remarks = Column(Text, nullable=True)

    __table_args__ = (
        Index('packaging_label_idx', 'label'),
    )