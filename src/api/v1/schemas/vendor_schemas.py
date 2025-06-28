from typing import List, Optional
from uuid import UUID
import re

from pydantic import BaseModel, Field, field_validator

from .base_schemas import CreateBaseSchema, UpdateBaseSchema, TimeStampedSchema


class VendorCreateSchema(CreateBaseSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Vendor name")
    email: Optional[str] = Field(None, max_length=255, description="Vendor email address")
    address: Optional[str] = Field(None, description="Vendor address")
    remarks: Optional[str] = Field(None, max_length=255, description="Additional remarks")
    city: Optional[str] = Field(None, max_length=255, description="Vendor city")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        
        return v.lower().strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Vendor name cannot be empty")
        return v.strip()


class VendorUpdateSchema(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Vendor name")
    email: Optional[str] = Field(None, max_length=255, description="Vendor email address")
    address: Optional[str] = Field(None, description="Vendor address")
    remarks: Optional[str] = Field(None, max_length=255, description="Additional remarks")
    city: Optional[str] = Field(None, max_length=255, description="Vendor city")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError("Invalid email format")
        
        return v.lower().strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Vendor name cannot be empty")
        return v.strip() if v else None


class VendorResponseSchema(TimeStampedSchema):
    name: str
    email: Optional[str] = None
    address: Optional[str] = None
    remarks: Optional[str] = None
    city: Optional[str] = None


class VendorsListResponseSchema(BaseModel):
    vendors: List[VendorResponseSchema]
    total: int
    skip: int
    limit: int


class VendorSearchSchema(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    search_fields: Optional[List[str]] = Field(
        default=["name", "email", "city", "remarks"],
        description="Fields to search in"
    )
    limit: int = Field(default=10, ge=1, le=100, description="Maximum number of results")