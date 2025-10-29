from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.dependencies import get_session
from src.converter.repositories import ExchangeRateRepository, ExchangeRepository
from src.converter.service import CurrencyConverterService


def get_exchange_rate_repository(
    session: AsyncSession = Depends(get_session),
) -> ExchangeRateRepository:
    return ExchangeRateRepository(session)


def get_exchange_repository(
    session: AsyncSession = Depends(get_session),
) -> ExchangeRepository:
    return ExchangeRepository(session)


def get_currency_converter_service(
    exchange_rate_repo: Annotated[
        ExchangeRateRepository, Depends(get_exchange_rate_repository)
    ],
    exchange_repo: Annotated[ExchangeRepository, Depends(get_exchange_repository)],
) -> CurrencyConverterService:
    return CurrencyConverterService(exchange_rate_repo, exchange_repo)
