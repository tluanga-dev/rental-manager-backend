from fastapi import APIRouter

from .endpoints.customers import router as customers_router
from .endpoints.item_packaging import router as item_packaging_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(customers_router)
api_router.include_router(item_packaging_router)