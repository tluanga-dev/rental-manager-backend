from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from ....application.services.inventory_item_master_service import InventoryItemMasterService
from ....core.config.database import get_db_session
from ....infrastructure.repositories.inventory_item_master_repository_impl import SQLAlchemyInventoryItemMasterRepository
from ....infrastructure.database.models import InventoryItemMasterModel, ItemSubCategoryModel, ItemCategoryModel, UnitOfMeasurementModel, ItemPackagingModel, LineItemModel
from ..schemas.inventory_item_master_schemas import (
    InventoryItemMasterCreateSchema,
    InventoryItemMasterUpdateSchema,
    InventoryItemMasterResponseSchema,
    InventoryItemMastersListResponseSchema,
    InventoryItemMasterSearchSchema,
    InventoryItemMasterQuantityUpdateSchema,
    InventoryItemMasterDimensionsUpdateSchema,
    InventoryItemMasterStatsSchema,
)

router = APIRouter(prefix="/inventory-items", tags=["inventory-items"])


def get_inventory_item_master_service(db: Session = Depends(get_db_session)) -> InventoryItemMasterService:
    repository = SQLAlchemyInventoryItemMasterRepository(db)
    return InventoryItemMasterService(repository)


def inventory_item_to_response_schema(inventory_item) -> InventoryItemMasterResponseSchema:
    return InventoryItemMasterResponseSchema(
        id=inventory_item.id,
        name=inventory_item.name,
        sku=inventory_item.sku,
        description=inventory_item.description,
        contents=inventory_item.contents,
        item_sub_category_id=inventory_item.item_sub_category_id,
        unit_of_measurement_id=inventory_item.unit_of_measurement_id,
        packaging_id=inventory_item.packaging_id,
        tracking_type=inventory_item.tracking_type,
        is_consumable=inventory_item.is_consumable,
        brand=inventory_item.brand,
        manufacturer_part_number=inventory_item.manufacturer_part_number,
        product_id=inventory_item.product_id,
        weight=inventory_item.weight,
        length=inventory_item.length,
        width=inventory_item.width,
        height=inventory_item.height,
        renting_period=inventory_item.renting_period,
        quantity=inventory_item.quantity,
        created_at=inventory_item.created_at,
        updated_at=inventory_item.updated_at,
        created_by=inventory_item.created_by,
        is_active=inventory_item.is_active,
    )


def inventory_model_to_response_schema(model, line_items_count: int = 0) -> InventoryItemMasterResponseSchema:
    """Convert SQLAlchemy model to response schema with related names and line items count"""
    can_delete = line_items_count == 0
    
    return InventoryItemMasterResponseSchema(
        id=model.id,
        name=model.name,
        sku=model.sku,
        description=model.description,
        contents=model.contents,
        item_sub_category_id=model.item_sub_category_id,
        unit_of_measurement_id=model.unit_of_measurement_id,
        packaging_id=model.packaging_id,
        tracking_type=model.tracking_type.value,
        is_consumable=model.is_consumable,
        brand=model.brand,
        manufacturer_part_number=model.manufacturer_part_number,
        product_id=model.product_id,
        weight=model.weight,
        length=model.length,
        width=model.width,
        height=model.height,
        renting_period=model.renting_period,
        quantity=model.quantity,
        created_at=model.created_at,
        updated_at=model.updated_at,
        created_by=model.created_by,
        is_active=model.is_active,
        # Related names from joined tables
        item_category_name=model.subcategory.item_category.name if model.subcategory and model.subcategory.item_category else None,
        item_sub_category_name=model.subcategory.name if model.subcategory else None,
        unit_of_measurement_name=model.unit_of_measurement.name if model.unit_of_measurement else None,
        packaging_name=model.packaging.label if model.packaging else None,
        # Delete functionality fields
        line_items_count=line_items_count,
        can_delete=can_delete,
    )


@router.post("/", response_model=InventoryItemMasterResponseSchema, status_code=201)
async def create_inventory_item(
    item_data: InventoryItemMasterCreateSchema,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    try:
        inventory_item = await service.create_inventory_item_master(
            name=item_data.name,
            sku=item_data.sku,
            item_sub_category_id=item_data.item_sub_category_id,
            unit_of_measurement_id=item_data.unit_of_measurement_id,
            tracking_type=item_data.tracking_type,
            is_consumable=item_data.is_consumable,
            description=item_data.description,
            contents=item_data.contents,
            packaging_id=item_data.packaging_id,
            brand=item_data.brand,
            manufacturer_part_number=item_data.manufacturer_part_number,
            product_id=item_data.product_id,
            weight=item_data.weight,
            length=item_data.length,
            width=item_data.width,
            height=item_data.height,
            renting_period=item_data.renting_period,
            quantity=item_data.quantity,
            created_by=item_data.created_by
        )
        return inventory_item_to_response_schema(inventory_item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats", response_model=InventoryItemMasterStatsSchema)
async def get_inventory_item_stats(
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    """Get statistics for inventory item masters"""
    stats = await service.get_stats()
    return InventoryItemMasterStatsSchema(**stats)


@router.get("/{item_id}", response_model=InventoryItemMasterResponseSchema)
async def get_inventory_item(
    item_id: UUID,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    inventory_item = await service.get_inventory_item_master(item_id)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory_item_to_response_schema(inventory_item)


@router.get("/by-sku/{sku}", response_model=InventoryItemMasterResponseSchema)
async def get_inventory_item_by_sku(
    sku: str,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    inventory_item = await service.get_inventory_item_master_by_sku(sku)
    if not inventory_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return inventory_item_to_response_schema(inventory_item)


@router.put("/{item_id}", response_model=InventoryItemMasterResponseSchema)
async def update_inventory_item(
    item_id: UUID,
    item_data: InventoryItemMasterUpdateSchema,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    try:
        inventory_item = await service.update_inventory_item_master(
            inventory_item_id=item_id,
            name=item_data.name,
            sku=item_data.sku,
            description=item_data.description,
            contents=item_data.contents,
            item_sub_category_id=item_data.item_sub_category_id,
            unit_of_measurement_id=item_data.unit_of_measurement_id,
            packaging_id=item_data.packaging_id,
            tracking_type=item_data.tracking_type,
            is_consumable=item_data.is_consumable,
            brand=item_data.brand,
            manufacturer_part_number=item_data.manufacturer_part_number,
            product_id=item_data.product_id,
            weight=item_data.weight,
            length=item_data.length,
            width=item_data.width,
            height=item_data.height,
            renting_period=item_data.renting_period,
            quantity=item_data.quantity,
            is_active=item_data.is_active
        )
        return inventory_item_to_response_schema(inventory_item)
    except ValueError as e:
        raise HTTPException(status_code=404 if "not found" in str(e) else 400, detail=str(e))


@router.delete("/{item_id}", status_code=204)
async def delete_inventory_item(
    item_id: UUID,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    # Check if item exists
    item = await service.get_inventory_item_master(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Check if item can be deleted (no associated line items)
    can_delete = await service.can_delete_inventory_item_master(item_id)
    if not can_delete:
        line_items_count = await service.get_line_items_count(item_id)
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete inventory item. It has {line_items_count} associated line items. Remove all line items first."
        )
    
    # Proceed with deletion
    deleted = await service.delete_inventory_item_master(item_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete inventory item")


@router.get("/", response_model=InventoryItemMastersListResponseSchema)
def list_inventory_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_session),
):
    # Subquery to get line items count for each inventory item master
    line_items_subquery = db.query(
        LineItemModel.inventory_item_master_id,
        func.count(LineItemModel.id).label('line_items_count')
    ).filter(
        LineItemModel.is_active == True
    ).group_by(LineItemModel.inventory_item_master_id).subquery()
    
    # Query with joins to get related names and line items count
    query_result = db.query(
        InventoryItemMasterModel,
        func.coalesce(line_items_subquery.c.line_items_count, 0).label('line_items_count')
    ).options(
        joinedload(InventoryItemMasterModel.subcategory)
        .joinedload(ItemSubCategoryModel.item_category),
        joinedload(InventoryItemMasterModel.unit_of_measurement),
        joinedload(InventoryItemMasterModel.packaging)
    ).outerjoin(
        line_items_subquery,
        InventoryItemMasterModel.id == line_items_subquery.c.inventory_item_master_id
    ).filter(
        InventoryItemMasterModel.is_active == True
    ).offset(skip).limit(limit).all()
    
    # Get total count
    total = db.query(InventoryItemMasterModel)\
        .filter(InventoryItemMasterModel.is_active == True).count()
    
    # Convert to response schemas with related names and line items count
    item_responses = [
        inventory_model_to_response_schema(model, line_items_count) 
        for model, line_items_count in query_result
    ]
    
    return InventoryItemMastersListResponseSchema(
        items=item_responses,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/by-subcategory/{subcategory_id}", response_model=List[InventoryItemMasterResponseSchema])
async def list_by_subcategory(
    subcategory_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    inventory_items = await service.list_by_subcategory(subcategory_id, skip, limit)
    return [inventory_item_to_response_schema(item) for item in inventory_items]


@router.get("/by-tracking-type/{tracking_type}", response_model=List[InventoryItemMasterResponseSchema])
async def list_by_tracking_type(
    tracking_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    if tracking_type not in ["BULK", "INDIVIDUAL"]:
        raise HTTPException(status_code=400, detail="Invalid tracking type. Must be BULK or INDIVIDUAL")
    
    inventory_items = await service.list_by_tracking_type(tracking_type, skip, limit)
    return [inventory_item_to_response_schema(item) for item in inventory_items]


@router.get("/consumables/", response_model=List[InventoryItemMasterResponseSchema])
async def list_consumables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    inventory_items = await service.list_consumables(skip, limit)
    return [inventory_item_to_response_schema(item) for item in inventory_items]


@router.get("/search/", response_model=List[InventoryItemMasterResponseSchema])
async def search_inventory_items(
    query: str = Query(..., min_length=1, description="Search query"),
    search_fields: Optional[List[str]] = Query(None, description="Fields to search in"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    inventory_items = await service.search_inventory_item_masters(query, search_fields, limit)
    return [inventory_item_to_response_schema(item) for item in inventory_items]


@router.patch("/{item_id}/quantity", response_model=dict)
async def update_quantity(
    item_id: UUID,
    quantity_data: InventoryItemMasterQuantityUpdateSchema,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    updated = await service.update_quantity(item_id, quantity_data.quantity)
    if not updated:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Quantity updated successfully", "new_quantity": quantity_data.quantity}


@router.patch("/{item_id}/dimensions", response_model=InventoryItemMasterResponseSchema)
async def update_dimensions(
    item_id: UUID,
    dimensions_data: InventoryItemMasterDimensionsUpdateSchema,
    service: InventoryItemMasterService = Depends(get_inventory_item_master_service),
):
    try:
        inventory_item = await service.update_dimensions(
            inventory_item_id=item_id,
            weight=dimensions_data.weight,
            length=dimensions_data.length,
            width=dimensions_data.width,
            height=dimensions_data.height
        )
        return inventory_item_to_response_schema(inventory_item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))