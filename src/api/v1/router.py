from fastapi import APIRouter

from .endpoints.customers import router as customers_router
from .endpoints.vendors import router as vendors_router
from .endpoints.item_categories import router as item_categories_router
from .endpoints.inventory_item_masters import router as inventory_item_masters_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(customers_router)
api_router.include_router(vendors_router)
api_router.include_router(item_categories_router)
api_router.include_router(inventory_item_masters_router)