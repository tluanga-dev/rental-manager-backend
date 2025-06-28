from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....application.services.vendor_service import VendorService
from ....core.config.database import get_db_session
from ....infrastructure.repositories.vendor_repository_impl import SQLAlchemyVendorRepository
from ..schemas.vendor_schemas import (
    VendorCreateSchema,
    VendorUpdateSchema,
    VendorResponseSchema,
    VendorsListResponseSchema,
    VendorSearchSchema,
)

router = APIRouter(prefix="/vendors", tags=["vendors"])


def get_vendor_service(db: Session = Depends(get_db_session)) -> VendorService:
    vendor_repository = SQLAlchemyVendorRepository(db)
    return VendorService(vendor_repository)


def vendor_to_response_schema(vendor) -> VendorResponseSchema:
    return VendorResponseSchema(
        id=vendor.id,
        name=vendor.name,
        email=vendor.email,
        address=vendor.address,
        remarks=vendor.remarks,
        city=vendor.city,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
        created_by=vendor.created_by,
        is_active=vendor.is_active,
    )


@router.post("/", response_model=VendorResponseSchema, status_code=201)
async def create_vendor(
    vendor_data: VendorCreateSchema,
    vendor_service: VendorService = Depends(get_vendor_service),
):
    try:
        vendor = await vendor_service.create_vendor(
            name=vendor_data.name,
            email=vendor_data.email,
            address=vendor_data.address,
            remarks=vendor_data.remarks,
            city=vendor_data.city,
            created_by=vendor_data.created_by
        )
        
        return vendor_to_response_schema(vendor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{vendor_id}", response_model=VendorResponseSchema)
async def get_vendor(
    vendor_id: UUID,
    vendor_service: VendorService = Depends(get_vendor_service),
):
    vendor = await vendor_service.get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return vendor_to_response_schema(vendor)


@router.put("/{vendor_id}", response_model=VendorResponseSchema)
async def update_vendor(
    vendor_id: UUID,
    vendor_data: VendorUpdateSchema,
    vendor_service: VendorService = Depends(get_vendor_service),
):
    try:
        vendor = await vendor_service.update_vendor(
            vendor_id=vendor_id,
            name=vendor_data.name,
            email=vendor_data.email,
            address=vendor_data.address,
            remarks=vendor_data.remarks,
            city=vendor_data.city,
            is_active=vendor_data.is_active
        )
        
        return vendor_to_response_schema(vendor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{vendor_id}", status_code=204)
async def delete_vendor(
    vendor_id: UUID,
    vendor_service: VendorService = Depends(get_vendor_service),
):
    deleted = await vendor_service.delete_vendor(vendor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vendor not found")


@router.get("/", response_model=VendorsListResponseSchema)
async def list_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vendor_service: VendorService = Depends(get_vendor_service),
):
    vendors = await vendor_service.list_vendors(skip=skip, limit=limit)
    
    vendor_responses = [vendor_to_response_schema(vendor) for vendor in vendors]
    
    return VendorsListResponseSchema(
        vendors=vendor_responses,
        total=len(vendor_responses),
        skip=skip,
        limit=limit,
    )


@router.get("/search/", response_model=List[VendorResponseSchema])
async def search_vendors(
    query: str = Query(..., min_length=1, description="Search query"),
    search_fields: Optional[List[str]] = Query(None, description="Fields to search in"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    vendor_service: VendorService = Depends(get_vendor_service),
):
    vendors = await vendor_service.search_vendors(query, search_fields, limit)
    return [vendor_to_response_schema(vendor) for vendor in vendors]


@router.get("/by-email/{email}", response_model=VendorResponseSchema)
async def get_vendor_by_email(
    email: str,
    vendor_service: VendorService = Depends(get_vendor_service),
):
    vendor = await vendor_service.get_vendor_by_email(email)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return vendor_to_response_schema(vendor)


@router.get("/by-city/{city}", response_model=List[VendorResponseSchema])
async def get_vendors_by_city(
    city: str,
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of results"),
    vendor_service: VendorService = Depends(get_vendor_service),
):
    vendors = await vendor_service.get_vendors_by_city(city, limit)
    return [vendor_to_response_schema(vendor) for vendor in vendors]