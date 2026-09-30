"""TSETMC MCP Server: داده قیمت و اطلاعات شرکت را به‌صورت ابزار MCP استاندارد ارائه می‌دهد."""
from mcp.server.fastmcp import FastMCP

from market_analyst.config import get_settings
from market_analyst.data.market_context_service import get_latest_real_money_ratio
from market_analyst.data.service import get_symbol
from market_analyst.logging import setup_logging

setup_logging(get_settings().log_level)

mcp = FastMCP("tsetmc")


@mcp.tool()
async def get_symbol_data(symbol: str) -> dict:
    """داده قیمت تاریخی و اطلاعات شرکت یک نماد را از TSETMC برمی‌گرداند."""
    data = await get_symbol(symbol)
    return {
        "instrument": data.instrument.model_dump(),
        "prices": [p.model_dump(mode="json") for p in data.prices],
        "source": data.source,
        "stale": data.stale,
    }


@mcp.tool()
async def get_real_money_ratio(ins_code: str) -> dict:
    """نسبت خالص جریان پول حقیقی برای یک نماد بر اساس ins_code."""
    ratio = await get_latest_real_money_ratio(ins_code)
    return {"ins_code": ins_code, "real_money_net_ratio": ratio}


if __name__ == "__main__":
    mcp.run()