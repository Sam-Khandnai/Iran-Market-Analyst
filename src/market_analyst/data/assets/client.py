import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from market_analyst.config import Settings, get_settings
from market_analyst.data.errors import TransientError, TSETMCError


class NavasanClient:
    def __init__(self, settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None):
        self._s = settings or get_settings()
        self._http = httpx.AsyncClient(timeout=self._s.http_timeout_seconds, transport=transport)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _fetch(self) -> dict:
        if not self._s.navasan_api_key:
            raise TSETMCError("NAVASAN_API_KEY تنظیم نشده است")
        try:
            r = await self._http.get(self._s.navasan_api_url, params={"api_key": self._s.navasan_api_key})
        except httpx.TransportError as e:
            raise TransientError(f"network error: {e}") from e
        if r.status_code == 429 or r.status_code >= 500:
            raise TransientError(f"{r.status_code} from navasan")
        if r.status_code >= 400:
            raise TSETMCError(f"{r.status_code} from navasan")
        try:
            data = r.json()
        except ValueError as e:
            raise TSETMCError("پاسخ نوسان JSON نیست") from e
        if not isinstance(data, dict):
            raise TSETMCError("پاسخ نوسان غیرمنتظره است")
        return data

    async def latest(self) -> dict:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(self._s.http_max_retries),
            wait=wait_exponential(multiplier=self._s.retry_backoff_seconds, max=20),
            retry=retry_if_exception_type(TransientError),
            reraise=True,
        ):
            with attempt:
                return await self._fetch()
        raise TSETMCError("unreachable")  # pragma: no cover