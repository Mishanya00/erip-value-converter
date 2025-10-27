import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from tenacity import RetryError

from src.repository.repositories import ExchangeRateRepository
from src.config import settings
from src.client.currency_rate_client import CurrencyRateClient
from src.converter.exceptions import ExternalAPIRequestError


class CurrencyConverterService:
    def __init__(self, exchange_rate_repo: ExchangeRateRepository):
        self.timezone = ZoneInfo(settings.TIMEZONE)
        self.logger = logging.getLogger(__name__)
        self.exchange_rate_repo = exchange_rate_repo

    async def get_currency_rates_request(self, period: int = 0):
        async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
            try:
                response = await aclient.get_rates(period)
            except RetryError as e:
                self.logger.exception(f"Failed to get currency rates: {e}")
                raise ExternalAPIRequestError
        return response.json()

    async def get_today_currency_rates(self):
        date = datetime.now(self.timezone).date()
        rates = await self.exchange_rate_repo.get_rates_by_cur_date(date)
        if not rates:
            async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
                try:
                    response = await aclient.get_rates()
                except RetryError as e:
                    self.logger.exception(f"Failed to get currency rates: {e}")
                    raise ExternalAPIRequestError
        return response.json()