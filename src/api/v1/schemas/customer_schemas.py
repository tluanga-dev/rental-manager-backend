from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, EmailStr
from .base_schemas import TimeStampedSchema, CreateBaseSchema, UpdateBaseSchema
from .contact_number_schemas import ContactNumberResponseSchema


class AddressSchema(BaseModel):
    street: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=50)
    zip_code: str = Field(..., min_length=1, max_length=20)
    country: str = Field(default="USA", max_length=100)

    @validator('street', 'city', 'state', 'zip_code')
    def validate_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()


class CustomerCreateSchema(CreateBaseSchema):
    name: str = Field(..., min_length=2, max_length=255, description="Customer name")
    email: Optional[str] = Field(None, max_length=255, description="Customer email address")
    address: Optional[str] = Field(None, description="Customer address")
    remarks: Optional[str] = Field(None, max_length=255, description="Additional remarks")
    city: Optional[str] = Field(None, max_length=255, description="Customer city")
    
    # Backward compatibility
    address_vo: Optional[AddressSchema] = Field(None, description="Structured address (backward compatibility)")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        
        import re
        v = v.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

    @validator('city')
    def validate_city(cls, v):
        if v is None:
            return v
        return v.strip().title()


class CustomerUpdateSchema(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=2, max_length=255, description="Customer name")
    email: Optional[str] = Field(None, max_length=255, description="Customer email address")
    address: Optional[str] = Field(None, description="Customer address")
    remarks: Optional[str] = Field(None, max_length=255, description="Additional remarks")
    city: Optional[str] = Field(None, max_length=255, description="Customer city")
    
    # Backward compatibility
    address_vo: Optional[AddressSchema] = Field(None, description="Structured address (backward compatibility)")

    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip() if v else v

    @validator('email')
    def validate_email(cls, v):
        if v is None:
            return v
        
        import re
        v = v.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v

    @validator('city')
    def validate_city(cls, v):
        if v is None:
            return v
        return v.strip().title()


class CustomerResponseSchema(TimeStampedSchema):
    name: str
    email: Optional[str] = None
    address: Optional[str] = None
    remarks: Optional[str] = None
    city: Optional[str] = None
    
    # Backward compatibility
    address_vo: Optional[AddressSchema] = None
    
    # Contact numbers
    contact_numbers: Optional[List[ContactNumberResponseSchema]] = None


class CustomersListResponseSchema(BaseModel):
    customers: List[CustomerResponseSchema]
    total: int
    skip: int
    limit: int


class CustomerSearchSchema(BaseModel):
    query: str = Field(..., min_length=1, description="Search query")
    search_fields: Optional[List[str]] = Field(None, description="Fields to search in")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")

    @validator('search_fields')
    def validate_search_fields(cls, v):
        if v is None:
            return ["name", "email", "city", "remarks"]
        
        allowed_fields = ["name", "email", "city", "remarks"]
        for field in v:
            if field not in allowed_fields:
                raise ValueError(f'Invalid search field: {field}. Allowed: {", ".join(allowed_fields)}')
        return v


class CustomerStatisticsSchema(BaseModel):
    total_customers: int
    customers_with_email: int
    customers_with_city: int
    recent_customers_30_days: int
    city_distribution: dict
    top_cities: List[tuple]


class CustomerWithContactsSchema(BaseModel):
    customer: CustomerResponseSchema
    contact_count: int
    contact_numbers: List[str]


class CustomerBulkCreateSchema(BaseModel):
    customers: List[CustomerCreateSchema] = Field(..., min_items=1, max_items=100)
    skip_duplicates: bool = Field(True, description="Skip duplicate entries instead of failing")