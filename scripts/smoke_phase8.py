import asyncio

from market_analyst.graph.mcp_adapters import mcp_fetch_real_money, mcp_fetch_symbol


async def main(symbol: str = "فولاد") -> None:
    data = await mcp_fetch_symbol(symbol)
    print("از طریق MCP:", data.instrument.name, "| تعداد کندل:", len(data.prices))
    ratio = await mcp_fetch_real_money(data.instrument.ins_code)
    print("real_money_net_ratio (MCP):", ratio)


if __name__ == "__main__":
    asyncio.run(main())
