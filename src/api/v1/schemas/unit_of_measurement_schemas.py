from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema


class UnitOfMeasurementBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the unit of measurement")
    abbreviation: str = Field(..., min_length=1, max_length=8, description="Abbreviation for the unit")
    description: Optional[str] = Field(None, description="Description of the unit of measurement")

    @validator('name', 'abbreviation')
    def strip_whitespace(cls, v):
        return v.strip() if v else v

    @validator('abbreviation')
    def validate_abbreviation_length(cls, v):
        if v and len(v.strip()) > 8:
            raise ValueError('Abbreviation cannot exceed 8 characters')
        return v

    class Config:
        from_attributes = True


class UnitOfMeasurementCreate(UnitOfMeasurementBase, CreateBaseSchema):
    pass


class UnitOfMeasurementUpdate(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the unit of measurement")
    abbreviation: Optional[str] = Field(None, min_length=1, max_length=8, description="Abbreviation for the unit")
    description: Optional[str] = Field(None, description="Description of the unit of measurement")

    @validator('name', 'abbreviation')
    def strip_whitespace(cls, v):
        return v.strip() if v else v

    @validator('abbreviation')
    def validate_abbreviation_length(cls, v):
        if v and len(v.strip()) > 8:
            raise ValueError('Abbreviation cannot exceed 8 characters')
        return v


class UnitOfMeasurement(UnitOfMeasurementBase, TimeStampedSchema):
    pass


class UnitOfMeasurementResponse(UnitOfMeasurement):
    class Config:
        from_attributes = True
