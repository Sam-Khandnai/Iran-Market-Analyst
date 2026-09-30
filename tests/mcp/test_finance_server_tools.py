from datetime import UTC, datetime

from market_analyst.data.models import Instrument, SymbolData
from market_analyst.mcp_servers import finance_server
from tests.engines.conftest import make_prices


async def _fake_get_symbol(symbol: str) -> SymbolData:
    inst = Instrument(ins_code="1", symbol=symbol, name="تست", eps=500, sector_pe=8)
    return SymbolData(
        instrument=inst, prices=make_prices([1000]),
        source="tsetmc", fetched_at=datetime.now(UTC),
    )


async def test_get_basic_fundamentals_tool(monkeypatch):
    monkeypatch.setattr(finance_server, "get_symbol", _fake_get_symbol)
    result = await finance_server.get_basic_fundamentals("فولاد")
    assert result["eps"] == 500
    assert result["sector_pe"] == 8