from datetime import UTC, datetime

from market_analyst.data.models import Instrument, SymbolData
from market_analyst.mcp_servers import tsetmc_server
from tests.engines.conftest import make_prices


async def _fake_get_symbol(symbol: str) -> SymbolData:
    inst = Instrument(ins_code="1", symbol=symbol, name="تست")
    return SymbolData(
        instrument=inst, prices=make_prices([1000, 1010]),
        source="tsetmc", fetched_at=datetime.now(UTC),
    )


async def _fake_real_money(ins_code: str) -> float:
    return 0.2


async def test_get_symbol_data_tool_returns_json_serializable_dict(monkeypatch):
    monkeypatch.setattr(tsetmc_server, "get_symbol", _fake_get_symbol)
    result = await tsetmc_server.get_symbol_data("فولاد")
    assert result["instrument"]["symbol"] == "فولاد"
    assert len(result["prices"]) == 2
    assert isinstance(result["prices"][0]["trade_date"], str)


async def test_get_real_money_ratio_tool(monkeypatch):
    monkeypatch.setattr(tsetmc_server, "get_latest_real_money_ratio", _fake_real_money)
    result = await tsetmc_server.get_real_money_ratio("222")
    assert result["real_money_net_ratio"] == 0.2