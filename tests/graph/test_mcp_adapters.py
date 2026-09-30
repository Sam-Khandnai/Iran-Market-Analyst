import pytest

from market_analyst.data.errors import SymbolNotFound
from market_analyst.graph import mcp_adapters


class FakeClient:
    def __init__(self, responses: dict):
        self._responses = responses

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def call(self, tool: str, **kwargs):
        value = self._responses[tool]
        if isinstance(value, Exception):
            raise value
        return value


async def test_mcp_fetch_symbol_maps_response(monkeypatch):
    fake = FakeClient({
        "get_symbol_data": {
            "instrument": {"ins_code": "1", "symbol": "فولاد", "name": "تست"},
            "prices": [{
                "ins_code": "1", "trade_date": "2024-01-01",
                "open": 1000, "high": 1010, "low": 990, "close": 1005,
                "last": 1005, "yesterday": 1000, "volume": 100, "value": 100000, "trades": 5,
            }],
            "stale": False,
        }
    })
    monkeypatch.setattr(mcp_adapters, "MCPToolClient", lambda module: fake)
    result = await mcp_adapters.mcp_fetch_symbol("فولاد")
    assert result.instrument.symbol == "فولاد"
    assert len(result.prices) == 1


async def test_mcp_fetch_symbol_raises_symbol_not_found(monkeypatch):
    fake = FakeClient({"get_symbol_data": RuntimeError("نماد «ناموجود» پیدا نشد.")})
    monkeypatch.setattr(mcp_adapters, "MCPToolClient", lambda module: fake)
    with pytest.raises(SymbolNotFound):
        await mcp_adapters.mcp_fetch_symbol("ناموجود")


async def test_mcp_fetch_real_money(monkeypatch):
    fake = FakeClient({"get_real_money_ratio": {"real_money_net_ratio": 0.33}})
    monkeypatch.setattr(mcp_adapters, "MCPToolClient", lambda module: fake)
    ratio = await mcp_adapters.mcp_fetch_real_money("222")
    assert ratio == 0.33