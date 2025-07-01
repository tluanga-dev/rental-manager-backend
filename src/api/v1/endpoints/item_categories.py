from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ....application.services.item_category_service import ItemCategoryService, ItemSubCategoryService
from ....core.config.database import get_db_session
from ....infrastructure.repositories.item_category_repository_impl import (
    SQLAlchemyItemCategoryRepository,
    SQLAlchemyItemSubCategoryRepository
)
from ..schemas.item_category_schemas import (
    ItemCategoryCreateSchema,
    ItemCategoryUpdateSchema,
    ItemCategoryResponseSchema,
    ItemCategoriesListResponseSchema,
    ItemSubCategoryCreateSchema,
    ItemSubCategoryUpdateSchema,
    ItemSubCategoryResponseSchema,
    ItemSubCategoriesListResponseSchema,
    ItemCategoryWithSubcategoriesResponseSchema,
)

router = APIRouter(prefix="/item-categories", tags=["item-categories"])


def get_category_service(db: Session = Depends(get_db_session)) -> ItemCategoryService:
    category_repository = SQLAlchemyItemCategoryRepository(db)
    return ItemCategoryService(category_repository)


def get_subcategory_service(db: Session = Depends(get_db_session)) -> ItemSubCategoryService:
    category_repository = SQLAlchemyItemCategoryRepository(db)
    subcategory_repository = SQLAlchemyItemSubCategoryRepository(db)
    return ItemSubCategoryService(subcategory_repository, category_repository)


def category_to_response_schema(category, subcategory_count: int = 0) -> ItemCategoryResponseSchema:
    return ItemCategoryResponseSchema(
        id=category.id,
        name=category.name,
        abbreviation=category.abbreviation,
        description=category.description,
        subcategory_count=subcategory_count,
        created_at=category.created_at,
        updated_at=category.updated_at,
        created_by=category.created_by,
        is_active=category.is_active,
    )


def subcategory_to_response_schema(subcategory) -> ItemSubCategoryResponseSchema:
    return ItemSubCategoryResponseSchema(
        id=subcategory.id,
        name=subcategory.name,
        abbreviation=subcategory.abbreviation,
        description=subcategory.description,
        item_category_id=subcategory.item_category_id,
        created_at=subcategory.created_at,
        updated_at=subcategory.updated_at,
        created_by=subcategory.created_by,
        is_active=subcategory.is_active,
    )


# Item Category endpoints

@router.post("/", response_model=ItemCategoryResponseSchema, status_code=201)
async def create_category(
    category_data: ItemCategoryCreateSchema,
    category_service: ItemCategoryService = Depends(get_category_service),
):
    try:
        category = await category_service.create_category(
            name=category_data.name,
            abbreviation=category_data.abbreviation,
            description=category_data.description,
            created_by=category_data.created_by
        )
        
        return category_to_response_schema(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{category_id}", response_model=ItemCategoryResponseSchema)
async def get_category(
    category_id: str,
    category_service: ItemCategoryService = Depends(get_category_service),
):
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category_to_response_schema(category)


@router.put("/{category_id}", response_model=ItemCategoryResponseSchema)
async def update_category(
    category_id: str,
    category_data: ItemCategoryUpdateSchema,
    category_service: ItemCategoryService = Depends(get_category_service),
):
    try:
        category = await category_service.update_category(
            category_id=category_id,
            name=category_data.name,
            abbreviation=category_data.abbreviation,
            description=category_data.description,
            is_active=category_data.is_active
        )
        
        return category_to_response_schema(category)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: str,
    category_service: ItemCategoryService = Depends(get_category_service),
):
    deleted = await category_service.delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")


@router.get("/", response_model=ItemCategoriesListResponseSchema)
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category_service: ItemCategoryService = Depends(get_category_service),
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    categories = await category_service.list_categories(skip=skip, limit=limit)
    
    # Get subcategory counts for each category
    category_responses = []
    for category in categories:
        # Count active subcategories for this category
        subcategory_count = await subcategory_service.count_subcategories_by_category(category.id)
        category_responses.append(category_to_response_schema(category, subcategory_count))
    
    return ItemCategoriesListResponseSchema(
        categories=category_responses,
        total=len(category_responses),
        skip=skip,
        limit=limit,
    )


@router.get("/search/", response_model=List[ItemCategoryResponseSchema])
async def search_categories(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    category_service: ItemCategoryService = Depends(get_category_service),
):
    categories = await category_service.search_categories(query, limit)
    return [category_to_response_schema(category) for category in categories]


@router.get("/stats/overview")
async def get_category_statistics(
    category_service: ItemCategoryService = Depends(get_category_service),
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    """Get comprehensive category and subcategory statistics."""
    # Get all categories and subcategories
    categories = await category_service.list_categories(skip=0, limit=1000)
    subcategories = await subcategory_service.list_subcategories(skip=0, limit=1000)
    
    # Calculate statistics
    total_categories = len(categories)
    active_categories = len([c for c in categories if c.is_active])
    inactive_categories = total_categories - active_categories
    
    total_subcategories = len(subcategories)
    
    # Count categories with subcategories
    categories_with_subcategories = 0
    for category in categories:
        subcategory_count = await subcategory_service.count_subcategories_by_category(category.id)
        if subcategory_count > 0:
            categories_with_subcategories += 1
    
    # Count categories/subcategories with descriptions
    categories_with_description = len([c for c in categories if c.description])
    subcategories_with_description = len([s for s in subcategories if s.description])
    
    # Abbreviation distribution
    abbreviation_distribution = {}
    for category in categories:
        abbrev = category.abbreviation
        abbreviation_distribution[abbrev] = abbreviation_distribution.get(abbrev, 0) + 1
    
    # Top abbreviations (by frequency)
    top_abbreviations = [
        {"abbreviation": abbrev, "count": count}
        for abbrev, count in sorted(abbreviation_distribution.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Recent items (simplified - just use total for now)
    recent_categories_30_days = total_categories
    recent_subcategories_30_days = total_subcategories
    
    return {
        "total_categories": total_categories,
        "active_categories": active_categories,
        "inactive_categories": inactive_categories,
        "total_subcategories": total_subcategories,
        "categories_with_subcategories": categories_with_subcategories,
        "categories_with_description": categories_with_description,
        "subcategories_with_description": subcategories_with_description,
        "abbreviation_distribution": abbreviation_distribution,
        "recent_categories_30_days": recent_categories_30_days,
        "recent_subcategories_30_days": recent_subcategories_30_days,
        "top_abbreviations": top_abbreviations,
    }


@router.get("/by-name/{name}", response_model=ItemCategoryResponseSchema)
async def get_category_by_name(
    name: str,
    category_service: ItemCategoryService = Depends(get_category_service),
):
    category = await category_service.get_category_by_name(name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category_to_response_schema(category)


@router.get("/by-abbreviation/{abbreviation}", response_model=ItemCategoryResponseSchema)
async def get_category_by_abbreviation(
    abbreviation: str,
    category_service: ItemCategoryService = Depends(get_category_service),
):
    category = await category_service.get_category_by_abbreviation(abbreviation)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category_to_response_schema(category)


# Item SubCategory endpoints

@router.post("/subcategories/", response_model=ItemSubCategoryResponseSchema, status_code=201)
async def create_subcategory(
    subcategory_data: ItemSubCategoryCreateSchema,
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    try:
        subcategory = await subcategory_service.create_subcategory(
            name=subcategory_data.name,
            abbreviation=subcategory_data.abbreviation,
            item_category_id=subcategory_data.item_category_id,
            description=subcategory_data.description,
            created_by=subcategory_data.created_by
        )
        
        return subcategory_to_response_schema(subcategory)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/subcategories/{subcategory_id}", response_model=ItemSubCategoryResponseSchema)
async def get_subcategory(
    subcategory_id: str,
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    subcategory = await subcategory_service.get_subcategory(subcategory_id)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    return subcategory_to_response_schema(subcategory)


@router.put("/subcategories/{subcategory_id}", response_model=ItemSubCategoryResponseSchema)
async def update_subcategory(
    subcategory_id: str,
    subcategory_data: ItemSubCategoryUpdateSchema,
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    try:
        subcategory = await subcategory_service.update_subcategory(
            subcategory_id=subcategory_id,
            name=subcategory_data.name,
            abbreviation=subcategory_data.abbreviation,
            item_category_id=subcategory_data.item_category_id,
            description=subcategory_data.description,
            is_active=subcategory_data.is_active
        )
        
        return subcategory_to_response_schema(subcategory)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/subcategories/{subcategory_id}", status_code=204)
async def delete_subcategory(
    subcategory_id: str,
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    deleted = await subcategory_service.delete_subcategory(subcategory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subcategory not found")


@router.get("/subcategories/", response_model=ItemSubCategoriesListResponseSchema)
async def list_subcategories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    subcategories = await subcategory_service.list_subcategories(skip=skip, limit=limit)
    
    subcategory_responses = [subcategory_to_response_schema(subcategory) for subcategory in subcategories]
    
    return ItemSubCategoriesListResponseSchema(
        subcategories=subcategory_responses,
        total=len(subcategory_responses),
        skip=skip,
        limit=limit,
    )


@router.get("/{category_id}/subcategories/", response_model=List[ItemSubCategoryResponseSchema])
async def get_subcategories_by_category(
    category_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    subcategories = await subcategory_service.get_subcategories_by_category(category_id, skip, limit)
    return [subcategory_to_response_schema(subcategory) for subcategory in subcategories]


@router.get("/subcategories/search/", response_model=List[ItemSubCategoryResponseSchema])
async def search_subcategories(
    query: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    subcategories = await subcategory_service.search_subcategories(query, category_id, limit)
    return [subcategory_to_response_schema(subcategory) for subcategory in subcategories]


@router.get("/subcategories/by-abbreviation/{abbreviation}", response_model=ItemSubCategoryResponseSchema)
async def get_subcategory_by_abbreviation(
    abbreviation: str,
    subcategory_service: ItemSubCategoryService = Depends(get_subcategory_service),
):
    subcategory = await subcategory_service.get_subcategory_by_abbreviation(abbreviation)
    if not subcategory:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    return subcategory_to_response_schema(subcategory)