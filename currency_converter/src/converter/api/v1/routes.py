from typing import Annotated

from fastapi import APIRouter, Depends

from src.converter.service import CurrencyConverterService
from src.converter.api.v1.schemas import ExchangeMoneyRequestSchema
from src.converter.dependencies import get_currency_converter_service


converter_router_v1 = APIRouter()


@converter_router_v1.get("/")
async def root():
    return {"message": "Currency Converter version 1"}


@converter_router_v1.get("/today")
async def get_today_rates(
    currency_converter_service: Annotated[
        CurrencyConverterService, Depends(get_currency_converter_service)
    ],
):
    return await currency_converter_service.get_today_currency_rates()


@converter_router_v1.post("/exchange_currency")
async def exchange_currency(
    exchange: ExchangeMoneyRequestSchema,
    currency_converter_service: Annotated[
        CurrencyConverterService, Depends(get_currency_converter_service)
    ],
):
    return await currency_converter_service.execute_currency_exchange(
        exchange.source_cur_amount,
        exchange.source_cur_abbreviation,
        exchange.target_cur_abbreviation,
    )
