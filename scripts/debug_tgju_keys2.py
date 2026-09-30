import asyncio
import httpx

GUESSES = [
    "nim", "sekee_1", "azad1", "bahar_azadi", "azadi1", "azadi",
    "rob", "nim_azadi", "rob_azadi", "sekee_ni", "sekee_rob",
    "azad", "sekeb", "sekke_azadi1",
]

async def main() -> None:
    async with httpx.AsyncClient(timeout=20) as client:
        for key in GUESSES:
            r = await client.get(
                f"https://api.tgju.org/v1/market/indicator/summary-table-data/{key}",
                params={"start": "0", "length": "1"},
            )
            ok = r.status_code == 200 and '"data":[' in r.text and '"data":[]' not in r.text
            print(f"{key:15s} -> status={r.status_code} valid_data={ok}")

if __name__ == "__main__":
    asyncio.run(main())
