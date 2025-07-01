from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema


class ItemPackagingBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the packaging")
    label: str = Field(..., min_length=1, max_length=255, description="Unique label for the packaging")
    unit: str = Field(..., min_length=1, max_length=255, description="Unit of measurement")
    remarks: Optional[str] = Field(None, description="Additional remarks about the packaging")

    @validator('label')
    def normalize_label(cls, v):
        return v.upper() if v else v

    @validator('name', 'unit')
    def strip_whitespace(cls, v):
        return v.strip() if v else v

    class Config:
        from_attributes = True


class ItemPackagingCreate(ItemPackagingBase, CreateBaseSchema):
    pass


class ItemPackagingUpdate(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the packaging")
    label: Optional[str] = Field(None, min_length=1, max_length=255, description="Unique label for the packaging")
    unit: Optional[str] = Field(None, min_length=1, max_length=255, description="Unit of measurement")
    remarks: Optional[str] = Field(None, description="Additional remarks about the packaging")

    @validator('label')
    def normalize_label(cls, v):
        return v.upper() if v else v

    @validator('name', 'unit')
    def strip_whitespace(cls, v):
        return v.strip() if v else v


class ItemPackaging(ItemPackagingBase, TimeStampedSchema):
    pass


class ItemPackagingResponse(ItemPackaging):
    class Config:
        from_attributes = True
