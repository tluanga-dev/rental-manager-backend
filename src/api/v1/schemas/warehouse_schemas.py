from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema


class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the warehouse")
    label: str = Field(..., min_length=1, max_length=255, description="Unique label for the warehouse")
    remarks: Optional[str] = Field(None, description="Additional remarks about the warehouse")

    @validator('label')
    def normalize_label(cls, v):
        return v.upper() if v else v

    @validator('name')
    def strip_whitespace(cls, v):
        return v.strip() if v else v

    class Config:
        from_attributes = True


class WarehouseCreate(WarehouseBase, CreateBaseSchema):
    pass


class WarehouseUpdate(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the warehouse")
    label: Optional[str] = Field(None, min_length=1, max_length=255, description="Unique label for the warehouse")
    remarks: Optional[str] = Field(None, description="Additional remarks about the warehouse")

    @validator('label')
    def normalize_label(cls, v):
        return v.upper() if v else v

    @validator('name')
    def strip_whitespace(cls, v):
        return v.strip() if v else v


class Warehouse(WarehouseBase, TimeStampedSchema):
    pass


class WarehouseResponse(Warehouse):
    class Config:
        from_attributes = True
