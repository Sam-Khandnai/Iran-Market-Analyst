# scripts/smoke_client_type.py
import asyncio

from market_analyst.data.market_context_service import get_latest_real_money_ratio
from market_analyst.data.service import get_symbol


async def main(symbol: str = "فولاد") -> None:
    data = await get_symbol(symbol)
    ratio = await get_latest_real_money_ratio(data.instrument.ins_code)
    print("real_money_net_ratio:", ratio)


if __name__ == "__main__":
    asyncio.run(main())