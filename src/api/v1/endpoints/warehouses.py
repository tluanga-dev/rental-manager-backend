from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....core.config.database import get_db_session
from ....infrastructure.repositories.warehouse_repository_impl import WarehouseRepositoryImpl
from ....application.services.warehouse_service import WarehouseService
from ....application.use_cases.warehouse_use_cases import WarehouseUseCases
from ..schemas.warehouse_schemas import (
    Warehouse,
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
)

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


def get_warehouse_use_cases(db: Session = Depends(get_db_session)) -> WarehouseUseCases:
    repository = WarehouseRepositoryImpl(db)
    service = WarehouseService(repository)
    return WarehouseUseCases(service)


@router.post("/", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(
    warehouse_data: WarehouseCreate,
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Create a new warehouse"""
    try:
        warehouse = await use_cases.create_warehouse(
            name=warehouse_data.name,
            label=warehouse_data.label,
            remarks=warehouse_data.remarks,
            created_by=warehouse_data.created_by,
        )
        return WarehouseResponse.from_orm(warehouse)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Get warehouse by ID"""
    warehouse = await use_cases.get_warehouse(warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return WarehouseResponse.from_orm(warehouse)


@router.get("/")
async def list_warehouses(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=1000, description="Number of records per page"),
    is_active: bool = Query(True, description="Whether to return only active records"),
    search: str = Query(None, description="Search term for name or label"),
    ordering: str = Query("-created_at", description="Ordering field"),
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """List all warehouses with pagination"""
    skip = (page - 1) * page_size
    
    # If search is provided, use search functionality
    if search:
        warehouses = await use_cases.search_warehouses(search, skip, page_size)
    else:
        warehouses = await use_cases.list_warehouses(skip, page_size, active_only=is_active)
    
    # For now, return a simple count (we'll add a proper count method later)
    total_count = len(warehouses)
    
    # Sort results based on ordering parameter
    if ordering == "name":
        warehouses.sort(key=lambda x: x.name)
    elif ordering == "-name":
        warehouses.sort(key=lambda x: x.name, reverse=True)
    elif ordering == "label":
        warehouses.sort(key=lambda x: x.label)
    elif ordering == "-label":
        warehouses.sort(key=lambda x: x.label, reverse=True)
    elif ordering == "created_at":
        warehouses.sort(key=lambda x: x.created_at)
    elif ordering == "-created_at":
        warehouses.sort(key=lambda x: x.created_at, reverse=True)
    
    # Calculate pagination info
    has_next = len(warehouses) == page_size  # Simple heuristic
    has_previous = skip > 0
    
    next_url = f"/api/v1/warehouses/?page={page + 1}&page_size={page_size}&is_active={is_active}" if has_next else None
    previous_url = f"/api/v1/warehouses/?page={page - 1}&page_size={page_size}&is_active={is_active}" if has_previous else None
    
    return {
        "count": total_count,
        "next": next_url,
        "previous": previous_url,
        "results": [WarehouseResponse.from_orm(w).dict() for w in warehouses]
    }


@router.get("/search/", response_model=List[WarehouseResponse])
async def search_warehouses(
    name: str = Query(..., min_length=1, description="Name to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Search warehouses by name"""
    warehouses = await use_cases.search_warehouses(name, skip, limit)
    return [WarehouseResponse.from_orm(warehouse) for warehouse in warehouses]


@router.get("/label/{label}", response_model=WarehouseResponse)
async def get_warehouse_by_label(
    label: str,
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Get warehouse by label"""
    warehouse = await use_cases.get_warehouse_by_label(label)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return WarehouseResponse.from_orm(warehouse)


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: UUID,
    warehouse_data: WarehouseUpdate,
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Update an existing warehouse"""
    try:
        warehouse = await use_cases.update_warehouse(
            warehouse_id=warehouse_id,
            name=warehouse_data.name,
            label=warehouse_data.label,
            remarks=warehouse_data.remarks,
        )
        return WarehouseResponse.from_orm(warehouse)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.patch("/{warehouse_id}/deactivate", status_code=204)
async def deactivate_warehouse(
    warehouse_id: UUID,
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Deactivate a warehouse (soft delete)"""
    try:
        await use_cases.deactivate_warehouse(warehouse_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{warehouse_id}/activate", status_code=204)
async def activate_warehouse(
    warehouse_id: UUID,
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Activate a warehouse"""
    try:
        await use_cases.activate_warehouse(warehouse_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats/overview")
async def get_warehouse_stats(
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """Get warehouse statistics for overview"""
    try:
        # Get all active warehouses to calculate stats
        all_warehouses = await use_cases.list_warehouses(skip=0, limit=10000, active_only=True)
        
        total_warehouses = len(all_warehouses)
        warehouses_with_remarks = len([w for w in all_warehouses if w.remarks and w.remarks.strip()])
        
        # Calculate recent warehouses (30 days) - using timezone-aware datetime
        from datetime import datetime, timedelta, timezone
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        recent_warehouses_30_days = len([w for w in all_warehouses if w.created_at >= thirty_days_ago])
        
        return {
            "total_warehouses": total_warehouses,
            "warehouses_with_remarks": warehouses_with_remarks,
            "recent_warehouses_30_days": recent_warehouses_30_days,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")
