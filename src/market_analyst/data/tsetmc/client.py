from urllib.parse import quote

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from market_analyst.config import Settings, get_settings
from market_analyst.data.errors import TransientError, TSETMCError
from market_analyst.logging import get_logger

log = get_logger("tsetmc")


class TSETMCClient:
    def __init__(
        self,
        settings: Settings | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ):
        self._s = settings or get_settings()
        self._http = httpx.AsyncClient(
            base_url=self._s.tsetmc_api_url,
            timeout=self._s.http_timeout_seconds,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; market-analyst/0.1)",
                "Accept": "application/json",
            },
            transport=transport,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _fetch(self, path: str) -> dict:
        try:
            r = await self._http.get(path)
        except httpx.TransportError as e:
            raise TransientError(f"network error on {path}: {e}") from e
        if r.status_code == 429 or r.status_code >= 500:
            raise TransientError(f"{r.status_code} on {path}")
        if r.status_code >= 400:
            raise TSETMCError(f"{r.status_code} on {path}")
        try:
            data = r.json()
        except ValueError as e:
            raise TSETMCError(f"پاسخ JSON نیست (احتمالاً بلاک/HTML): {path}") from e
        if not isinstance(data, dict):
            raise TSETMCError(f"پاسخ غیرمنتظره از {path}")
        return data

    async def _get_json(self, path: str) -> dict:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._s.http_max_retries),
            wait=wait_exponential(multiplier=self._s.retry_backoff_seconds, max=20),
            retry=retry_if_exception_type(TransientError),
            reraise=True,
        ):
            with attempt:
                log.debug("tsetmc_get", path=path, attempt=attempt.retry_state.attempt_number)
                return await self._fetch(path)
        raise TSETMCError("unreachable")  # pragma: no cover

    async def search(self, query: str) -> dict:
        return await self._get_json(f"/Instrument/GetInstrumentSearch/{quote(query)}")

    async def instrument_info(self, ins_code: str) -> dict:
        return await self._get_json(f"/Instrument/GetInstrumentInfo/{ins_code}")

    async def daily_prices(self, ins_code: str, days: int = 0) -> dict:
        """days=0 یعنی کل تاریخچه."""
        return await self._get_json(f"/ClosingPrice/GetClosingPriceDailyList/{ins_code}/{days}")

    async def client_type_history(self, ins_code: str) -> dict:
        return await self._get_json(f"/ClientType/GetClientTypeHistory/{ins_code}")