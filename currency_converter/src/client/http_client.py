from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed


class BaseHTTPClient:
    def __init__(
        self,
        base_url: str,
    ):
        """Base http client. Takes base_url as an argument."""
        self.base_url = base_url
        self._client = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
            )

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError(
                "Client not connected. Use 'async with' or call connect() first."
            )
        return self._client

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        response = await self.client.get(
            endpoint,
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response
