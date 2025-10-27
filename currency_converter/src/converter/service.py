import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from tenacity import RetryError

from src.converter.api.v1.schemas import ExchangeRateBaseSchema
from src.converter.repositories import ExchangeRateRepository
from src.converter.exceptions import ExternalAPIRequestError
from src.config import settings
from src.client.currency_rate_client import CurrencyRateClient
from src.client.schemas import ExternalAPIExchangeRateSchema


class CurrencyConverterService:
    def __init__(self, exchange_rate_repo: ExchangeRateRepository):
        self.timezone = ZoneInfo(settings.TIMEZONE)
        self.logger = logging.getLogger(__name__)
        self.exchange_rate_repo = exchange_rate_repo

    async def get_currency_rates_request(self, period: int = 0) -> list[ExternalAPIExchangeRateSchema]:
        async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
            try:
                currency_rates: list[ExternalAPIExchangeRateSchema] = await aclient.get_rates(period)
            except RetryError as e:
                self.logger.exception(f"Failed to get currency rates: {e}")
                raise ExternalAPIRequestError
        return currency_rates

    async def get_today_currency_rates(self):
        date = datetime.now(self.timezone).date()
        rates = await self.exchange_rate_repo.get_rates_by_cur_date(date)
        if not rates:
            async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
                try:
                    currency_rates: list[ExternalAPIExchangeRateSchema] = await aclient.get_rates()

                    rates_to_create: list[ExchangeRateBaseSchema] = [
                        ExchangeRateBaseSchema(
                            cur_id=currency_rate.id,
                            cur_abbreviation=currency_rate.abbreviation,
                            cur_scale=currency_rate.scale,
                            cur_name=currency_rate.name,
                            cur_official_rate=currency_rate.rate,
                            cur_date=currency_rate.timestamp.date()
                        )
                        for currency_rate in currency_rates
                    ]

                    await self.exchange_rate_repo.insert_many_rates(rates_to_create)

                except RetryError as e:
                    self.logger.exception(f"Failed to get currency rates: {e}")
                    raise ExternalAPIRequestError
        return rates_to_create