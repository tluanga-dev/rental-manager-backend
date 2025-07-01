from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class TimeStampedSchema(BaseModel):
    id: str = Field(..., description="UUID as string")
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    is_active: bool = True

    @validator('id')
    def validate_uuid_format(cls, v):
        """Validate that id is a valid UUID string format"""
        import uuid
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError('Invalid UUID format')

    class Config:
        from_attributes = True


class CreateBaseSchema(BaseModel):
    created_by: Optional[str] = Field(None, description="User who created this record")
    is_active: bool = Field(True, description="Whether this record is active")


class UpdateBaseSchema(BaseModel):
    is_active: Optional[bool] = Field(None, description="Whether this record is active")