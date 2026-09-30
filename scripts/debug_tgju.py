import asyncio
import httpx


async def main() -> None:
    async with httpx.AsyncClient(timeout=20) as client:
        # حدس ۱: صفحه سابقه دلار
        r1 = await client.get(
            "https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl",
            params={"start": "0", "length": "10"},
        )
        print("=== summary-table-data ===")
        print(r1.status_code, r1.text[:1500])

        print()
        # حدس ۲: نمودار تاریخی
        r2 = await client.get(
            "https://api.tgju.org/v1/data/chart",
            params={"item": "price_dollar_rl", "type": "history"},
        )
        print("=== chart ===")
        print(r2.status_code, r2.text[:1500])


if __name__ == "__main__":
    asyncio.run(main())
