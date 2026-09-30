from market_analyst.data.errors import DataError
from market_analyst.engines.decision.engine import DecisionEngine
from market_analyst.engines.decision.models import DecisionInput
from market_analyst.engines.errors import InsufficientHistoryError
from market_analyst.engines.fundamental.engine import FundamentalEngine
from market_analyst.engines.fundamental.models import FundamentalInput
from market_analyst.engines.market_context.engine import MarketContextEngine
from market_analyst.engines.market_context.models import MarketContextInput
from market_analyst.engines.news.engine import NewsEngine
from market_analyst.engines.risk.engine import RiskEngine
from market_analyst.engines.risk.models import RiskInput
from market_analyst.engines.technical.engine import TechnicalEngine
from market_analyst.graph.chart_builder import build_chart_series
from market_analyst.graph.state import GraphState, as_of_date
from market_analyst.rag.retriever import Retriever
from market_analyst.schemas.report import AnalysisReport, Decision


def make_data_node(fetch_symbol, fetch_real_money):
    async def data_node(state: GraphState) -> dict:
        try:
            data = await fetch_symbol(state["symbol"])
        except DataError as e:
            return {"errors": [f"data: {e}"], "prices": [], "instrument": None}
        try:
            ratio = await fetch_real_money(data.instrument.ins_code)
        except DataError:
            ratio = None
        return {"instrument": data.instrument, "prices": data.prices, "real_money_net_ratio": ratio}

    return data_node


async def technical_node(state: GraphState) -> dict:
    prices = state.get("prices") or []
    if not prices:
        return {"errors": ["technical: no price data"], "technical": None}
    try:
        return {"technical": TechnicalEngine().analyze(state["symbol"], prices)}
    except InsufficientHistoryError as e:
        return {"errors": [f"technical: {e}"], "technical": None}


async def fundamental_node(state: GraphState) -> dict:
    inst, prices = state.get("instrument"), state.get("prices") or []
    if inst is None or not prices:
        return {"fundamental": None}
    data = FundamentalInput(
        symbol=state["symbol"], as_of=as_of_date(state),
        price=prices[-1].close, eps=inst.eps, sector_pe=inst.sector_pe,
    )
    return {"fundamental": FundamentalEngine().analyze(data)}


async def market_context_node(state: GraphState) -> dict:
    prices = state.get("prices") or []
    if not prices:
        return {"market_context": None}
    data = MarketContextInput(
        symbol=state["symbol"], as_of=as_of_date(state),
        real_money_net_ratio=state.get("real_money_net_ratio"),
    )
    return {"market_context": MarketContextEngine().analyze(data)}


def make_news_node(retriever: Retriever):
    async def news_node(state: GraphState) -> dict:
        chunks = await retriever.retrieve(
            query=state["symbol"], doc_type="news", symbol=state["symbol"], top_k=5,
        )
        return {"news": NewsEngine().analyze(state["symbol"], as_of_date(state), chunks)}

    return news_node



async def risk_node(state: GraphState) -> dict:
    prices = state.get("prices") or []
    avg_value = sum(p.value for p in prices[-20:]) / len(prices[-20:]) if prices else None
    data = RiskInput(
        symbol=state["symbol"], as_of=as_of_date(state),
        technical=state.get("technical"), fundamental=state.get("fundamental"),
        market_context=state.get("market_context"),
        avg_daily_value_rial=avg_value, free_float_ratio=None,
    )
    return {"risk": RiskEngine().analyze(data)}


async def decision_node(state: GraphState) -> dict:
    data = DecisionInput(
        symbol=state["symbol"], as_of=as_of_date(state),
        technical=state.get("technical"), fundamental=state.get("fundamental"),
        market_context=state.get("market_context"), risk=state.get("risk"),
    )
    return {"decision": DecisionEngine().analyze(data)}


def make_explanation_node(explanation_agent, retriever: Retriever | None = None):
    async def explanation_node(state: GraphState) -> dict:
        decision = state.get("decision")
        retrieved_context: list[str] | None = None
        if retriever is not None:
            chunks = await retriever.retrieve(query=state["symbol"], symbol=state["symbol"], top_k=3)
            if chunks:
                retrieved_context = [c.chunk.text for c in chunks]

        summary = await explanation_agent.explain(decision, state.get("risk"), retrieved_context)
        report = AnalysisReport(
            symbol=state["symbol"],
            technical_analysis=state["technical"].model_dump() if state.get("technical") else {},
            fundamental_analysis=state["fundamental"].model_dump() if state.get("fundamental") else {},
            market_context=state["market_context"].model_dump() if state.get("market_context") else {},
            news_analysis=state["news"].model_dump() if state.get("news") else {},
            risk_analysis=state["risk"].model_dump() if state.get("risk") else {},
            decision=Decision(signal=decision.signal, confidence=decision.confidence) if decision else None,
            key_factors=decision.key_factors if decision else [],
            risks=decision.risks if decision else [],
            evidence=[],
            summary=summary,
            chart_data=build_chart_series(state.get("prices") or []),
        )
        return {"report": report}

    return explanation_node