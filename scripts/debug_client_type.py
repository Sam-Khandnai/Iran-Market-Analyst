import asyncio
import json

from market_analyst.data.tsetmc.client import TSETMCClient


async def main(ins_code: str = "46348559193224090") -> None:
    async with TSETMCClient() as c:
        raw = await c.client_type_history(ins_code)
        print(json.dumps(raw, ensure_ascii=False, indent=2)[:2000])
        print("---")
        print("keys:", list(raw.keys()))


if __name__ == "__main__":
    asyncio.run(main())
