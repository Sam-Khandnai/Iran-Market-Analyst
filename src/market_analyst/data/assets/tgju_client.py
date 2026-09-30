import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from market_analyst.config import Settings, get_settings
from market_analyst.data.errors import TransientError, TSETMCError


class TGJUClient:
    BASE_URL = "https://api.tgju.org/v1/market/indicator/summary-table-data"

    def __init__(self, settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None):
        self._s = settings or get_settings()
        self._http = httpx.AsyncClient(
            timeout=self._s.http_timeout_seconds,
            headers={"User-Agent": "Mozilla/5.0 (compatible; market-analyst/0.1)"},
            transport=transport,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _fetch(self, item_key: str, length: int) -> dict:
        try:
            r = await self._http.get(
                f"{self.BASE_URL}/{item_key}", params={"start": "0", "length": str(length)},
            )
        except httpx.TransportError as e:
            raise TransientError(f"network error: {e}") from e
        if r.status_code == 429 or r.status_code >= 500:
            raise TransientError(f"{r.status_code} from tgju")
        if r.status_code >= 400:
            raise TSETMCError(f"{r.status_code} from tgju for {item_key}")
        try:
            data = r.json()
        except ValueError as e:
            raise TSETMCError(f"پاسخ tgju برای {item_key} JSON نیست") from e
        return data

    async def history(self, item_key: str, length: int = 730) -> dict:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._s.http_max_retries),
            wait=wait_exponential(multiplier=self._s.retry_backoff_seconds, max=20),
            retry=retry_if_exception_type(TransientError),
            reraise=True,
        ):
            with attempt:
                return await self._fetch(item_key, length)
        raise TSETMCError("unreachable")  # pragma: no cover
