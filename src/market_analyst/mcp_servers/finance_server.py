"""Finance MCP Server (stub). اتصال کامل به Codal در فاز جداگانه بعدی انجام می‌شود؛
فعلاً همان EPS/P/E صنعت موجود در TSETMC را زیر یک ابزار «مالی» مجزا عرضه می‌کند."""
from mcp.server.fastmcp import FastMCP

from market_analyst.config import get_settings
from market_analyst.data.service import get_symbol
from market_analyst.logging import setup_logging

setup_logging(get_settings().log_level)

mcp = FastMCP("finance")


@mcp.tool()
async def get_basic_fundamentals(symbol: str) -> dict:
    """اطلاعات بنیادی پایه یک نماد (EPS، P/E صنعت). صورت مالی کامل هنوز متصل نشده."""
    data = await get_symbol(symbol)
    return {
        "symbol": symbol,
        "eps": data.instrument.eps,
        "sector_pe": data.instrument.sector_pe,
        "price": data.prices[-1].close if data.prices else None,
        "note": "داده صورت مالی کامل (Codal) هنوز متصل نشده است.",
    }


if __name__ == "__main__":
    mcp.run()