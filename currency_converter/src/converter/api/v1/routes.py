from fastapi import APIRouter

from src.converter.service import get_currency_rates


converter_router_v1 = APIRouter()


@converter_router_v1.get("/")
async def root():
    return {"message": "Currency Converter version 1"}


@converter_router_v1.get("/rates")
async def get_rates(period: int = 0):
    return await get_currency_rates(period)
