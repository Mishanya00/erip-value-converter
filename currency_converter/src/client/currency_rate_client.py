from httpx import Response

from src.client.http_client import BaseHTTPClient


class CurrencyRateClient(BaseHTTPClient):
    async def get_rates(self, periodicity: int = 0) -> Response:
        response = await self.get("/exrates/rates", params={"periodicity": periodicity})
        return response
