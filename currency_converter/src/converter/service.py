from src.config import settings
from src.client.currency_rate_client import CurrencyRateClient


class CurrencyConverterService():
    async def get_currency_rates(period: int = 0):
        async with CurrencyRateClient(base_url=settings.EXTERNAL_API_URL) as aclient:
            response = await aclient.get_rates(period)
        return response.json()

    async def get_today_currency_rates(self):
        pass
