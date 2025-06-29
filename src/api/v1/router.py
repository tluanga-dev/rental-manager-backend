from fastapi import APIRouter

from .endpoints.customers import router as customers_router
from .endpoints.vendors import router as vendors_router
from .endpoints.item_categories import router as item_categories_router
from .endpoints.inventory_item_masters import router as inventory_item_masters_router
from .endpoints.purchase_orders import router as purchase_orders_router
from .endpoints.unit_of_measurement import router as unit_of_measurement_router
from .endpoints.item_packaging import router as item_packaging_router
from .endpoints.warehouses import router as warehouses_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(customers_router)
api_router.include_router(vendors_router)
api_router.include_router(item_categories_router)
api_router.include_router(inventory_item_masters_router)
api_router.include_router(purchase_orders_router)
api_router.include_router(unit_of_measurement_router)
api_router.include_router(item_packaging_router)
api_router.include_router(warehouses_router)