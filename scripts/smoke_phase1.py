import asyncio
import sys

from market_analyst.data.db.session import init_db
from market_analyst.data.service import get_symbol


async def main(symbol: str) -> None:
    await init_db()

    d = await get_symbol(symbol, refresh=True)
    print("منبع:", d.source, "| stale:", d.stale, "| ردشده:", d.dropped_rows)
    print(d.instrument.model_dump_json(indent=2, ensure_ascii=False))
    print("تعداد کندل:", len(d.prices), "|", d.prices[0].trade_date, "->", d.prices[-1].trade_date)
    for p in d.prices[-5:]:
        print(p.trade_date, p.open, p.high, p.low, p.close, p.volume)

    d2 = await get_symbol(symbol)
    print("فراخوانی دوم -> منبع:", d2.source)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "فولاد"))