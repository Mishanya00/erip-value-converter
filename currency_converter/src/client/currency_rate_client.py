from src.client.schemas import ExternalAPIRateSchema
from src.client.http_client import BaseHTTPClient


class CurrencyRateClient(BaseHTTPClient):
    async def get_rates(self, periodicity: int = 0) -> list[ExternalAPIRateSchema]:
        response = await self.get("/exrates/rates", params={"periodicity": periodicity})
        response.raise_for_status()
        raw_rates_list = response.json()

        validated_rates = [ExternalAPIRateSchema.model_validate(item) for item in raw_rates_list]

        return validated_rates
