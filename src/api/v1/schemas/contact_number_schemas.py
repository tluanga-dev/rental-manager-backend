from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator
from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema


class PhoneNumberSchema(BaseModel):
    number: str = Field(..., min_length=5, max_length=20, description="Phone number")

    @validator('number')
    def validate_phone_number(cls, v):
        import re
        if not v or not v.strip():
            raise ValueError('Phone number cannot be empty')
        
        # Clean the number
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Validate format
        pattern = r"^\+?1?\d{9,15}$"
        if not re.match(pattern, cleaned):
            raise ValueError('Invalid phone number format')
        
        return cleaned


class ContactNumberCreateSchema(CreateBaseSchema):
    number: str = Field(..., description="Phone number")
    entity_type: str = Field(..., min_length=1, max_length=50, description="Type of entity this contact belongs to")
    entity_id: UUID = Field(..., description="ID of the entity this contact belongs to")

    @validator('number')
    def validate_phone_number(cls, v):
        import re
        if not v or not v.strip():
            raise ValueError('Phone number cannot be empty')
        
        # Clean the number
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Validate format
        pattern = r"^\+?1?\d{9,15}$"
        if not re.match(pattern, cleaned):
            raise ValueError('Invalid phone number format')
        
        return cleaned

    @validator('entity_type')
    def validate_entity_type(cls, v):
        if not v or not v.strip():
            raise ValueError('Entity type cannot be empty')
        
        allowed_types = ["Customer", "User", "Supplier", "Property", "Unit"]
        if v not in allowed_types:
            raise ValueError(f'Invalid entity type. Must be one of: {", ".join(allowed_types)}')
        
        return v


class ContactNumberUpdateSchema(UpdateBaseSchema):
    number: Optional[str] = Field(None, description="Phone number")
    entity_type: Optional[str] = Field(None, min_length=1, max_length=50, description="Type of entity")
    entity_id: Optional[UUID] = Field(None, description="ID of the entity")

    @validator('number')
    def validate_phone_number(cls, v):
        if v is None:
            return v
        
        import re
        if not v or not v.strip():
            raise ValueError('Phone number cannot be empty')
        
        # Clean the number
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        
        # Validate format
        pattern = r"^\+?1?\d{9,15}$"
        if not re.match(pattern, cleaned):
            raise ValueError('Invalid phone number format')
        
        return cleaned

    @validator('entity_type')
    def validate_entity_type(cls, v):
        if v is None:
            return v
        
        if not v or not v.strip():
            raise ValueError('Entity type cannot be empty')
        
        allowed_types = ["Customer", "User", "Supplier", "Property", "Unit"]
        if v not in allowed_types:
            raise ValueError(f'Invalid entity type. Must be one of: {", ".join(allowed_types)}')
        
        return v


class ContactNumberResponseSchema(TimeStampedSchema):
    number: str
    entity_type: Optional[str]
    entity_id: Optional[UUID]
    
    # Helper properties
    formatted_number: Optional[str] = Field(None, description="Formatted phone number")
    international_format: Optional[str] = Field(None, description="International format")


class ContactNumberListResponseSchema(BaseModel):
    contact_numbers: List[ContactNumberResponseSchema]
    total: int
    skip: int
    limit: int


class EntityContactSummarySchema(BaseModel):
    entity_type: str
    entity_id: UUID
    total_contacts: int
    contact_numbers: List[ContactNumberResponseSchema]


class ContactNumberBulkCreateSchema(BaseModel):
    contact_numbers: List[ContactNumberCreateSchema] = Field(..., min_items=1, max_items=100)
    skip_duplicates: bool = Field(True, description="Skip duplicate entries instead of failing")


class ContactNumberSearchSchema(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")