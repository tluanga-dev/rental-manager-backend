from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TimeStampedSchema(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


class CreateBaseSchema(BaseModel):
    created_by: Optional[str] = Field(None, description="User who created this record")
    is_active: bool = Field(True, description="Whether this record is active")


class UpdateBaseSchema(BaseModel):
    is_active: Optional[bool] = Field(None, description="Whether this record is active")