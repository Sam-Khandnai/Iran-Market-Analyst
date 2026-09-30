import asyncio
import httpx

KEYS_TO_TEST = [
    "price_dollar_rl", "price_eur", "price_aed",
    "geram18", "sekee", "nim_sekee", "rob_sekee", "gerami",
    "ons",
]

async def main() -> None:
    async with httpx.AsyncClient(timeout=20) as client:
        for key in KEYS_TO_TEST:
            r = await client.get(
                f"https://api.tgju.org/v1/market/indicator/summary-table-data/{key}",
                params={"start": "0", "length": "2"},
            )
            ok = r.status_code == 200 and '"data":[' in r.text and '"data":[]' not in r.text
            print(f"{key:15s} -> status={r.status_code} valid_data={ok}")
            if ok:
                print("   sample:", r.text[:200])

if __name__ == "__main__":
    asyncio.run(main())
