from typing import Annotated

from fastapi import APIRouter, Depends

from src.converter.service import CurrencyConverterService
from src.converter.dependencies import get_currency_converter_service


converter_router_v1 = APIRouter()


@converter_router_v1.get("/")
async def root():
    return {"message": "Currency Converter version 1"}


@converter_router_v1.get("/rates")
async def get_rates(
        currency_converter_service: Annotated[CurrencyConverterService, Depends(get_currency_converter_service)],
        period: int = 0,
):
    return await currency_converter_service.get_currency_rates_request(period)

@converter_router_v1.get("/rates/today")
async def get_today_rates(
        currency_converter_service: Annotated[CurrencyConverterService, Depends(get_currency_converter_service)],
):
    return await currency_converter_service.get_today_currency_rates()