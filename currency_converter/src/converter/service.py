from src.repository.repositories import ExchangeRateRepository
from src.config import settings
from src.client.currency_rate_client import CurrencyRateClient


class CurrencyConverterService:
    def __init__(self, exchange_rate_repo: ExchangeRateRepository):
        self.exchange_rate_repo = exchange_rate_repo

    @staticmethod
    async def get_currency_rates_request(period: int = 0):
        async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
            response = await aclient.get_rates(period)
        return response.json()

    async def get_today_currency_rates(self):
        pass
