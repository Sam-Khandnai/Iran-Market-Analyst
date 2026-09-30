"""تبدیل پاسخ MCP به مدل‌های داخلی پروژه، تا Graph بین دسترسی مستقیم و MCP سوییچ کند."""
from datetime import UTC, datetime

from market_analyst.data.errors import SymbolNotFound, TSETMCError
from market_analyst.data.models import DailyPrice, Instrument, SymbolData
from market_analyst.mcp_clients.client import MCPToolClient

_TSETMC_SERVER = "market_analyst.mcp_servers.tsetmc_server"


async def mcp_fetch_symbol(symbol: str) -> SymbolData:
    async with MCPToolClient(_TSETMC_SERVER) as client:
        try:
            raw = await client.call("get_symbol_data", symbol=symbol)
        except RuntimeError as e:
            # محدودیت شناخته‌شده: تشخیص نوع خطا فعلاً بر اساس متن پیام است؛
            # در فاز بعد با کدهای خطای ساختاریافته MCP جایگزین می‌شود.
            if "پیدا نشد" in str(e):
                raise SymbolNotFound(symbol) from e
            raise TSETMCError(str(e)) from e

        return SymbolData(
            instrument=Instrument(**raw["instrument"]),
            prices=[DailyPrice(**p) for p in raw["prices"]],
            source="tsetmc",
            stale=raw.get("stale", False),
            fetched_at=datetime.now(UTC),
        )


async def mcp_fetch_real_money(ins_code: str) -> float | None:
    async with MCPToolClient(_TSETMC_SERVER) as client:
        raw = await client.call("get_real_money_ratio", ins_code=ins_code)
        return raw.get("real_money_net_ratio")