import asyncio
import json

from market_analyst.data.assets.client import NavasanClient


async def main() -> None:
    async with NavasanClient() as c:
        raw = await c.latest()
        for k in ["usd", "usd_sell", "usd_buy", "aed"]:
            print(k, "->", raw.get(k))


if __name__ == "__main__":
    asyncio.run(main())
