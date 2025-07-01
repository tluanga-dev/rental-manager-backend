from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.config.database import get_db_session
from ....infrastructure.repositories.item_packaging_repository_impl import ItemPackagingRepositoryImpl
from ....application.services.item_packaging_service import ItemPackagingService
from ....application.use_cases.item_packaging_use_cases import ItemPackagingUseCases
from ..schemas.item_packaging_schemas import (
    ItemPackaging,
    ItemPackagingCreate,
    ItemPackagingUpdate,
    ItemPackagingResponse,
)

router = APIRouter(prefix="/item-packaging", tags=["item-packaging"])


def get_item_packaging_use_cases(db: Session = Depends(get_db_session)) -> ItemPackagingUseCases:
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
    item_packaging_id: str,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Get item packaging by ID"""
    item_packaging = await use_cases.get_item_packaging(item_packaging_id)
    if not item_packaging:
        raise HTTPException(status_code=404, detail="Item packaging not found")
    return ItemPackagingResponse.from_orm(item_packaging)


@router.get("/")
async def list_item_packagings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=1000, description="Number of records per page"),
    is_active: bool = Query(True, description="Whether to return only active records"),
    search: str = Query(None, description="Search term for name or label"),
    ordering: str = Query("-created_at", description="Ordering field"),
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """List all item packagings with pagination"""
    skip = (page - 1) * page_size
    
    # If search is provided, use search functionality
    if search:
        item_packagings = await use_cases.search_item_packagings(search, skip, page_size)
    else:
        item_packagings = await use_cases.list_item_packagings(skip, page_size, active_only=is_active)
    
    # For now, return a simple count (we'll add a proper count method later)
    total_count = len(item_packagings)
    
    # Sort results based on ordering parameter
    if ordering == "name":
        item_packagings.sort(key=lambda x: x.name)
    elif ordering == "-name":
        item_packagings.sort(key=lambda x: x.name, reverse=True)
    elif ordering == "label":
        item_packagings.sort(key=lambda x: x.label)
    elif ordering == "-label":
        item_packagings.sort(key=lambda x: x.label, reverse=True)
    elif ordering == "unit":
        item_packagings.sort(key=lambda x: x.unit)
    elif ordering == "-unit":
        item_packagings.sort(key=lambda x: x.unit, reverse=True)
    elif ordering == "created_at":
        item_packagings.sort(key=lambda x: x.created_at)
    elif ordering == "-created_at":
        item_packagings.sort(key=lambda x: x.created_at, reverse=True)
    
    # Calculate pagination info
    has_next = len(item_packagings) == page_size  # Simple heuristic
    has_previous = skip > 0
    
    next_url = f"/api/v1/item-packaging/?page={page + 1}&page_size={page_size}&is_active={is_active}" if has_next else None
    previous_url = f"/api/v1/item-packaging/?page={page - 1}&page_size={page_size}&is_active={is_active}" if has_previous else None
    
    return {
        "count": total_count,
        "next": next_url,
        "previous": previous_url,
        "results": [ItemPackagingResponse.from_orm(ip).dict() for ip in item_packagings]
    }


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
    item_packaging_id: str,
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
    item_packaging_id: str,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Deactivate an item packaging (soft delete)"""
    try:
        await use_cases.deactivate_item_packaging(item_packaging_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{item_packaging_id}/activate", status_code=204)
async def activate_item_packaging(
    item_packaging_id: str,
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Activate an item packaging"""
    try:
        await use_cases.activate_item_packaging(item_packaging_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats/overview")
async def get_packaging_stats(
    use_cases: ItemPackagingUseCases = Depends(get_item_packaging_use_cases),
):
    """Get packaging statistics for overview"""
    try:
        # Get all active packagings to calculate stats
        all_packagings = await use_cases.list_item_packagings(skip=0, limit=10000, active_only=True)
        
        total_packaging = len(all_packagings)
        packaging_with_remarks = len([p for p in all_packagings if p.remarks and p.remarks.strip()])
        
        # Get unique units
        unique_units = len(set(p.unit for p in all_packagings))
        
        # Get units count for top units
        unit_counts = {}
        for p in all_packagings:
            unit_counts[p.unit] = unit_counts.get(p.unit, 0) + 1
        
        # Sort by count and get top units
        top_units = sorted(unit_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate recent packagings (30 days) - simplified for now
        from datetime import datetime, timedelta, timezone
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_packaging_30_days = len([p for p in all_packagings if p.created_at >= thirty_days_ago])
        
        return {
            "total_packaging": total_packaging,
            "packaging_with_remarks": packaging_with_remarks,
            "unique_units": unique_units,
            "recent_packaging_30_days": recent_packaging_30_days,
            "top_units": top_units[:5]  # Top 5 units
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")
