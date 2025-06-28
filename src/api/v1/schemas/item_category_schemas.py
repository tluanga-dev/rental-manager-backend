from typing import List, Optional
from uuid import UUID
import re

from pydantic import BaseModel, Field, field_validator

from .base_schemas import CreateBaseSchema, UpdateBaseSchema, TimeStampedSchema


class ItemCategoryCreateSchema(CreateBaseSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Category name")
    abbreviation: str = Field(..., min_length=1, max_length=9, description="Category abbreviation")
    description: Optional[str] = Field(None, description="Category description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Category name cannot be empty")
        return v.strip()

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Abbreviation cannot be empty")
        
        # Clean and uppercase
        abbreviation = v.strip().upper()
        
        if len(abbreviation) > 9:
            raise ValueError("Abbreviation cannot exceed 9 characters")
        
        return abbreviation


class ItemCategoryUpdateSchema(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Category name")
    abbreviation: Optional[str] = Field(None, min_length=1, max_length=9, description="Category abbreviation")
    description: Optional[str] = Field(None, description="Category description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Category name cannot be empty")
        return v.strip() if v else None

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Abbreviation cannot be empty")
            
            # Clean and uppercase
            abbreviation = v.strip().upper()
            
            if len(abbreviation) > 9:
                raise ValueError("Abbreviation cannot exceed 9 characters")
            
            return abbreviation
        return None


class ItemCategoryResponseSchema(TimeStampedSchema):
    name: str
    abbreviation: str
    description: Optional[str] = None


class ItemCategoriesListResponseSchema(BaseModel):
    categories: List[ItemCategoryResponseSchema]
    total: int
    skip: int
    limit: int


class ItemSubCategoryCreateSchema(CreateBaseSchema):
    name: str = Field(..., min_length=1, max_length=255, description="Subcategory name")
    abbreviation: str = Field(..., min_length=6, max_length=6, description="Subcategory abbreviation (exactly 6 characters)")
    description: Optional[str] = Field(None, description="Subcategory description")
    item_category_id: UUID = Field(..., description="Parent category ID")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Subcategory name cannot be empty")
        return v.strip()

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Abbreviation cannot be empty")
        
        # Clean and uppercase
        abbreviation = v.strip().upper()
        
        if len(abbreviation) != 6:
            raise ValueError("Abbreviation must be exactly 6 characters")
        
        if not any(c.isalpha() for c in abbreviation):
            raise ValueError("Abbreviation must contain at least one letter")
        
        return abbreviation


class ItemSubCategoryUpdateSchema(UpdateBaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Subcategory name")
    abbreviation: Optional[str] = Field(None, min_length=6, max_length=6, description="Subcategory abbreviation")
    description: Optional[str] = Field(None, description="Subcategory description")
    item_category_id: Optional[UUID] = Field(None, description="Parent category ID")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Subcategory name cannot be empty")
        return v.strip() if v else None

    @field_validator("abbreviation")
    @classmethod
    def validate_abbreviation(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Abbreviation cannot be empty")
            
            # Clean and uppercase
            abbreviation = v.strip().upper()
            
            if len(abbreviation) != 6:
                raise ValueError("Abbreviation must be exactly 6 characters")
            
            if not any(c.isalpha() for c in abbreviation):
                raise ValueError("Abbreviation must contain at least one letter")
            
            return abbreviation
        return None


class ItemSubCategoryResponseSchema(TimeStampedSchema):
    name: str
    abbreviation: str
    description: Optional[str] = None
    item_category_id: UUID
    item_category: Optional[ItemCategoryResponseSchema] = None  # Optional nested category


class ItemSubCategoriesListResponseSchema(BaseModel):
    subcategories: List[ItemSubCategoryResponseSchema]
    total: int
    skip: int
    limit: int


class ItemCategoryWithSubcategoriesResponseSchema(ItemCategoryResponseSchema):
    subcategories: List[ItemSubCategoryResponseSchema] = []