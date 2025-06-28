from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config.database import get_db_session
from ...infrastructure.repositories.warehouse_repository_impl import WarehouseRepositoryImpl
from ...application.services.warehouse_service import WarehouseService
from ...application.use_cases.warehouse_use_cases import WarehouseUseCases
from ..schemas.warehouse_schemas import (
    Warehouse,
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseResponse,
)

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


def get_warehouse_use_cases(db: AsyncSession = Depends(get_db_session)) -> WarehouseUseCases:
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


@router.get("/", response_model=List[WarehouseResponse])
async def list_warehouses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Whether to return only active records"),
    use_cases: WarehouseUseCases = Depends(get_warehouse_use_cases),
):
    """List all warehouses with pagination"""
    warehouses = await use_cases.list_warehouses(skip, limit, active_only)
    return [WarehouseResponse.from_orm(warehouse) for warehouse in warehouses]


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
