from fastapi import APIRouter

from src.converter.api.v1.routes import converter_router_v1


converter_router = APIRouter()

converter_router.include_router(converter_router_v1, prefix="/v1")
