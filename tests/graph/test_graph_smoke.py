from datetime import UTC, datetime

from market_analyst.data.errors import SymbolNotFound
from market_analyst.data.models import Instrument, SymbolData
from market_analyst.graph.build import build_graph
from market_analyst.rag.models import RetrievedChunk
from tests.engines.conftest import make_prices


async def fake_fetch_symbol(symbol: str) -> SymbolData:
    prices = make_prices([1000 * (1.01**i) for i in range(250)])
    inst = Instrument(ins_code="222", symbol=symbol, name="فولاد مبارکه", eps=500, sector_pe=8)
    return SymbolData(instrument=inst, prices=prices, source="tsetmc", fetched_at=datetime.now(UTC))


async def fake_fetch_real_money(ins_code: str) -> float:
    return 0.1


async def failing_fetch_symbol(symbol: str) -> SymbolData:
    raise SymbolNotFound(symbol)


class FakeLLM:
    async def ainvoke(self, prompt: str) -> str:
        return "خلاصه تستی"


class FakeRetriever:
    """جایگزین بدون اتصال به DB واقعی؛ از ساخت AsyncEngine در تست‌های واحد جلوگیری می‌کند."""

    async def retrieve(self, query, doc_type=None, symbol=None, top_k=5) -> list[RetrievedChunk]:
        return []


async def test_full_graph_produces_report():
    graph = build_graph(
        fetch_symbol=fake_fetch_symbol, fetch_real_money=fake_fetch_real_money,
        llm=FakeLLM(), retriever=FakeRetriever(),
    )
    result = await graph.ainvoke({"symbol": "فولاد", "errors": []})
    report = result["report"]
    assert report.symbol == "فولاد"
    assert report.decision is not None
    assert report.summary == "خلاصه تستی"
    assert report.technical_analysis["trend"] == "uptrend"


async def test_graph_falls_back_to_template_when_llm_none():
    graph = build_graph(
        fetch_symbol=fake_fetch_symbol, fetch_real_money=fake_fetch_real_money,
        llm=None, retriever=FakeRetriever(),
    )
    result = await graph.ainvoke({"symbol": "فولاد", "errors": []})
    assert "فولاد" in result["report"].summary


async def test_graph_degrades_gracefully_on_data_error():
    graph = build_graph(
        fetch_symbol=failing_fetch_symbol, fetch_real_money=fake_fetch_real_money,
        llm=FakeLLM(), retriever=FakeRetriever(),
    )
    result = await graph.ainvoke({"symbol": "ناموجود", "errors": []})
    assert result["report"] is not None
    assert result["report"].decision.signal.value == "WATCH"
    assert any("data:" in e for e in result["errors"])