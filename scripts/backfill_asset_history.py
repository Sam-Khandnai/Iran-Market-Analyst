import asyncio

from sqlalchemy.dialects.postgresql import insert

from market_analyst.data.assets.tgju_client import TGJUClient
from market_analyst.data.assets.tgju_parser import parse_history
from market_analyst.data.db.session import get_session_factory
from market_analyst.data.db.tables import AssetSnapshotRow
from market_analyst.data.errors import TSETMCError

TGJU_KEY_MAP: dict[str, str] = {
    "usd": "price_dollar_rl",
    "eur": "price_eur",
    "aed": "price_aed",
    "bub_18ayar": "geram18",
    "usd_xau": "ons",
    "bub_sekkeh": "sekee",
    "bub_gerami": "gerami",
    "bub_bahar": "sekeb",
    "bub_nim": "nim",
    "bub_rob": "rob",
}
async def backfill_one(key: str, tgju_key: str, client: TGJUClient) -> int:
    try:
        payload = await client.history(tgju_key, length=730)
    except TSETMCError as e:
        print(f"{key}: خطا در دریافت -> {e}")
        return 0

    rows, dropped = parse_history(payload)
    print(f"{key}: {len(rows)} ردیف دریافت شد, {dropped} ردیف نامعتبر")
    if not rows:
        return 0

    factory = get_session_factory()
    async with factory() as session:
        for r in rows:
            stmt = insert(AssetSnapshotRow).values(
                key=key, trade_date=r["trade_date"], value=r["close"], change=0.0,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=["key", "trade_date"], set_={"value": r["close"]},
            )
            await session.execute(stmt)
        await session.commit()
    return len(rows)


async def main() -> None:
    async with TGJUClient() as client:
        total = 0
        for key, tgju_key in TGJU_KEY_MAP.items():
            total += await backfill_one(key, tgju_key, client)
        print(f"\nجمع کل ردیف‌های ذخیره‌شده: {total}")


if __name__ == "__main__":
    asyncio.run(main())