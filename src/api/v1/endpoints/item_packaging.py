from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config.database import get_db_session
from ...infrastructure.repositories.item_packaging_repository_impl import ItemPackagingRepositoryImpl
from ...application.services.item_packaging_service import ItemPackagingService
from ...application.use_cases.item_packaging_use_cases import ItemPackagingUseCases
from ..schemas.item_packaging_schemas import (
    ItemPackaging,
    ItemPackagingCreate,
    ItemPackagingUpdate,
    ItemPackagingResponse,
)

router = APIRouter(prefix="/item-packaging", tags=["item-packaging"])


def get_item_packaging_use_cases(db: AsyncSession = Depends(get_db_session)) -> ItemPackagingUseCases:
    repository = ItemPackagingRepositoryImpl(db)
    service = ItemPackagingService(repository)
    return ItemPackagingUseCases(service)


@router.post("/", response_model=ItemPackagingResponse, status_code=201)
async def create_item_packaging(
    item_packaging_data: ItemPackagingCreate,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Create a new item packaging"""
    try:
        item_packaging = await use_cases.create_item_packaging(
            name=item_packaging_data.name,
            label=item_packaging_data.label,
            unit=item_packaging_data.unit,
            remarks=item_packaging_data.remarks,
            created_by=item_packaging_data.created_by,
        )
        return ItemPackagingResponse.from_orm(item_packaging)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{item_packaging_id}", response_model=ItemPackagingResponse)
async def get_item_packaging(
    item_packaging_id: UUID,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Get item packaging by ID"""
    item_packaging = await use_cases.get_item_packaging(item_packaging_id)
    if not item_packaging:
        raise HTTPException(status_code=404, detail="Item packaging not found")
    return ItemPackagingResponse.from_orm(item_packaging)


@router.get("/", response_model=List[ItemPackagingResponse])
async def list_item_packagings(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Whether to return only active records"),
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """List all item packagings with pagination"""
    item_packagings = await use_cases.list_item_packagings(skip, limit, active_only)
    return [ItemPackagingResponse.from_orm(ip) for ip in item_packagings]


@router.get("/search/", response_model=List[ItemPackagingResponse])
async def search_item_packagings(
    name: str = Query(..., min_length=1, description="Name to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Search item packagings by name"""
    item_packagings = await use_cases.search_item_packagings(name, skip, limit)
    return [ItemPackagingResponse.from_orm(ip) for ip in item_packagings]


@router.get("/label/{label}", response_model=ItemPackagingResponse)
async def get_item_packaging_by_label(
    label: str,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Get item packaging by label"""
    item_packaging = await use_cases.get_item_packaging_by_label(label)
    if not item_packaging:
        raise HTTPException(status_code=404, detail="Item packaging not found")
    return ItemPackagingResponse.from_orm(item_packaging)


@router.put("/{item_packaging_id}", response_model=ItemPackagingResponse)
async def update_item_packaging(
    item_packaging_id: UUID,
    item_packaging_data: ItemPackagingUpdate,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Update an existing item packaging"""
    try:
        item_packaging = await use_cases.update_item_packaging(
            item_packaging_id=item_packaging_id,
            name=item_packaging_data.name,
            label=item_packaging_data.label,
            unit=item_packaging_data.unit,
            remarks=item_packaging_data.remarks,
        )
        return ItemPackagingResponse.from_orm(item_packaging)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.patch("/{item_packaging_id}/deactivate", status_code=204)
async def deactivate_item_packaging(
    item_packaging_id: UUID,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Deactivate an item packaging (soft delete)"""
    try:
        await use_cases.deactivate_item_packaging(item_packaging_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{item_packaging_id}/activate", status_code=204)
async def activate_item_packaging(
    item_packaging_id: UUID,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Activate an item packaging"""
    try:
        await use_cases.activate_item_packaging(item_packaging_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
