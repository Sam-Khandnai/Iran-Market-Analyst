from datetime import UTC, datetime

from mcp.server.fastmcp import FastMCP

from market_analyst.config import get_settings
from market_analyst.logging import setup_logging

setup_logging(get_settings().log_level)

mcp = FastMCP("news")

@mcp.tool()
async def get_news_sentiment(symbol: str) -> dict:
    """اخبار و sentiment یک نماد؛ فعلاً همیشه خنثی است."""
    return {
        "symbol": symbol,
        "as_of": datetime.now(UTC).date().isoformat(),
        "sentiment": "neutral",
        "score": 50.0,
        "headlines": [],
        "coverage": 0.0,
    }


if __name__ == "__main__":
    mcp.run()