from typing import Literal

from langgraph.graph import END, START, StateGraph

from market_analyst.agents.explanation import ExplanationAgent
from market_analyst.data.market_context_service import get_latest_real_money_ratio
from market_analyst.data.service import get_symbol
from market_analyst.graph.nodes import (
    decision_node,
    fundamental_node,
    make_data_node,
    make_explanation_node,
    make_news_node,
    market_context_node,
    risk_node,
    technical_node,
)
from market_analyst.graph.state import GraphState
from market_analyst.llm.openrouter import ChatClient, build_default_llm
from market_analyst.rag.retriever import Retriever, build_default_retriever


def build_graph(
    fetch_symbol=None,
    fetch_real_money=None,
    llm: ChatClient | None | Literal["default"] = "default",
    retriever: Retriever | Literal["default"] = "default",
    use_mcp: bool = False,
):
    if fetch_symbol is None or fetch_real_money is None:
        if use_mcp:
            from market_analyst.graph.mcp_adapters import (
                mcp_fetch_real_money,
                mcp_fetch_symbol,
            )
            fetch_symbol = fetch_symbol or mcp_fetch_symbol
            fetch_real_money = fetch_real_money or mcp_fetch_real_money
        else:
            fetch_symbol = fetch_symbol or get_symbol
            fetch_real_money = fetch_real_money or get_latest_real_money_ratio

    resolved_llm = build_default_llm() if llm == "default" else llm
    resolved_retriever = build_default_retriever() if retriever == "default" else retriever

    g = StateGraph(GraphState)
    g.add_node("data", make_data_node(fetch_symbol, fetch_real_money))
    g.add_node("technical", technical_node)
    g.add_node("fundamental", fundamental_node)
    g.add_node("market_context", market_context_node)
    g.add_node("news", make_news_node(resolved_retriever))
    g.add_node("risk", risk_node)
    g.add_node("decision", decision_node)
    g.add_node("explanation", make_explanation_node(ExplanationAgent(resolved_llm), resolved_retriever))

    g.add_edge(START, "data")
    for branch in ("technical", "fundamental", "market_context", "news"):
        g.add_edge("data", branch)
        g.add_edge(branch, "risk")
    g.add_edge("risk", "decision")
    g.add_edge("decision", "explanation")
    g.add_edge("explanation", END)

    return g.compile()