import httpx
import pytest

from market_analyst.config import Settings
from market_analyst.data.errors import TransientError, TSETMCError
from market_analyst.data.tsetmc.client import TSETMCClient

FAST = Settings(http_max_retries=3, retry_backoff_seconds=0)


async def test_retries_on_503_then_succeeds():
    calls = {"n": 0}

    def handler(req: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, json={"instrumentSearch": []})

    async with TSETMCClient(FAST, transport=httpx.MockTransport(handler)) as c:
        assert await c.search("x") == {"instrumentSearch": []}
    assert calls["n"] == 3


async def test_gives_up_after_max_retries():
    async with TSETMCClient(FAST, transport=httpx.MockTransport(lambda r: httpx.Response(500))) as c:
        with pytest.raises(TransientError):
            await c.search("x")


async def test_html_response_is_error_not_retry():
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        return httpx.Response(200, text="<html>blocked</html>")

    async with TSETMCClient(FAST, transport=httpx.MockTransport(handler)) as c:
        with pytest.raises(TSETMCError):
            await c.search("x")
    assert calls["n"] == 1