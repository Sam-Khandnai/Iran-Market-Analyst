import asyncio

from market_analyst.graph.build import build_graph


async def main(symbol: str = "فولاد") -> None:
    graph = build_graph()  # llm="default" -> از .env خوانده می‌شود؛ اگر کلید نبود fallback فعال است
    result = await graph.ainvoke({"symbol": symbol, "errors": []})
    report = result["report"]
    print("signal:", report.decision.signal, "| confidence:", report.decision.confidence)
    print("summary:", report.summary)
    print("errors:", result["errors"])


if __name__ == "__main__":
    asyncio.run(main())
