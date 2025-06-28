from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config.database import get_db_session
from ...infrastructure.repositories.unit_of_measurement_repository_impl import UnitOfMeasurementRepositoryImpl
from ...application.services.unit_of_measurement_service import UnitOfMeasurementService
from ...application.use_cases.unit_of_measurement_use_cases import UnitOfMeasurementUseCases
from ..schemas.unit_of_measurement_schemas import (
    UnitOfMeasurement,
    UnitOfMeasurementCreate,
    UnitOfMeasurementUpdate,
    UnitOfMeasurementResponse,
)

router = APIRouter(prefix="/unit-of-measurement", tags=["unit-of-measurement"])


def get_unit_use_cases(db: AsyncSession = Depends(get_db_session)) -> UnitOfMeasurementUseCases:
    repository = UnitOfMeasurementRepositoryImpl(db)
    service = UnitOfMeasurementService(repository)
    return UnitOfMeasurementUseCases(service)


@router.post("/", response_model=UnitOfMeasurementResponse, status_code=201)
async def create_unit_of_measurement(
    unit_data: UnitOfMeasurementCreate,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Create a new unit of measurement"""
    try:
        unit = await use_cases.create_unit_of_measurement(
            name=unit_data.name,
            abbreviation=unit_data.abbreviation,
            description=unit_data.description,
            created_by=unit_data.created_by,
        )
        return UnitOfMeasurementResponse.from_orm(unit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{unit_id}", response_model=UnitOfMeasurementResponse)
async def get_unit_of_measurement(
    unit_id: UUID,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Get unit of measurement by ID"""
    unit = await use_cases.get_unit_of_measurement(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit of measurement not found")
    return UnitOfMeasurementResponse.from_orm(unit)


@router.get("/", response_model=List[UnitOfMeasurementResponse])
async def list_units_of_measurement(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    active_only: bool = Query(True, description="Whether to return only active records"),
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """List all units of measurement with pagination"""
    units = await use_cases.list_units_of_measurement(skip, limit, active_only)
    return [UnitOfMeasurementResponse.from_orm(unit) for unit in units]


@router.get("/search/", response_model=List[UnitOfMeasurementResponse])
async def search_units_of_measurement(
    name: str = Query(..., min_length=1, description="Name or abbreviation to search for"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Search units of measurement by name or abbreviation"""
    units = await use_cases.search_units_of_measurement(name, skip, limit)
    return [UnitOfMeasurementResponse.from_orm(unit) for unit in units]


@router.get("/name/{name}", response_model=UnitOfMeasurementResponse)
async def get_unit_by_name(
    name: str,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Get unit of measurement by name"""
    unit = await use_cases.get_unit_by_name(name)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit of measurement not found")
    return UnitOfMeasurementResponse.from_orm(unit)


@router.get("/abbreviation/{abbreviation}", response_model=UnitOfMeasurementResponse)
async def get_unit_by_abbreviation(
    abbreviation: str,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Get unit of measurement by abbreviation"""
    unit = await use_cases.get_unit_by_abbreviation(abbreviation)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit of measurement not found")
    return UnitOfMeasurementResponse.from_orm(unit)


@router.put("/{unit_id}", response_model=UnitOfMeasurementResponse)
async def update_unit_of_measurement(
    unit_id: UUID,
    unit_data: UnitOfMeasurementUpdate,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Update an existing unit of measurement"""
    try:
        unit = await use_cases.update_unit_of_measurement(
            unit_id=unit_id,
            name=unit_data.name,
            abbreviation=unit_data.abbreviation,
            description=unit_data.description,
        )
        return UnitOfMeasurementResponse.from_orm(unit)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.patch("/{unit_id}/deactivate", status_code=204)
async def deactivate_unit_of_measurement(
    unit_id: UUID,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Deactivate a unit of measurement (soft delete)"""
    try:
        await use_cases.deactivate_unit_of_measurement(unit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{unit_id}/activate", status_code=204)
async def activate_unit_of_measurement(
    unit_id: UUID,
    use_cases: UnitOfMeasurementUseCases = Depends(get_unit_use_cases),
):
    """Activate a unit of measurement"""
    try:
        await use_cases.activate_unit_of_measurement(unit_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
