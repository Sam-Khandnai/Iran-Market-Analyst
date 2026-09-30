import asyncio
import json

from market_analyst.data.assets.client import NavasanClient


async def main() -> None:
    async with NavasanClient() as c:
        raw = await c.latest()
        print(json.dumps(raw, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
