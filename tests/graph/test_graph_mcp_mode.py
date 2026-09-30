from datetime import UTC, datetime

from market_analyst.data.models import Instrument, SymbolData
from market_analyst.graph import mcp_adapters
from market_analyst.graph.build import build_graph
from tests.engines.conftest import make_prices
from tests.graph.test_graph_smoke import FakeRetriever


class FakeLLM:
    async def ainvoke(self, prompt: str) -> str:
        return "خلاصه تستی"


async def test_graph_uses_mcp_adapters_when_use_mcp_true(monkeypatch):
    async def fake_fetch_symbol(symbol: str) -> SymbolData:
        inst = Instrument(ins_code="1", symbol=symbol, name="تست", eps=100, sector_pe=8)
        return SymbolData(
            instrument=inst, prices=make_prices([1000] * 40),
            source="tsetmc", fetched_at=datetime.now(UTC),
        )

    async def fake_fetch_real_money(ins_code: str) -> float:
        return 0.1

    monkeypatch.setattr(mcp_adapters, "mcp_fetch_symbol", fake_fetch_symbol)
    monkeypatch.setattr(mcp_adapters, "mcp_fetch_real_money", fake_fetch_real_money)

    graph = build_graph(use_mcp=True, llm=FakeLLM(), retriever=FakeRetriever())
    result = await graph.ainvoke({"symbol": "فولاد", "errors": []})
    assert result["report"].symbol == "فولاد"
    assert result["report"].decision is not None