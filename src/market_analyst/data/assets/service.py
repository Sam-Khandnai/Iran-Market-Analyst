from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker

from market_analyst.data.assets.client import NavasanClient
from market_analyst.data.assets.models import AssetHistoryPoint, AssetQuote
from market_analyst.data.assets.parser import parse_quotes
from market_analyst.data.db.session import get_session_factory
from market_analyst.data.db.tables import AssetSnapshotRow
from market_analyst.data.errors import TSETMCError
from market_analyst.logging import get_logger

log = get_logger("assets.service")


async def get_all_quotes(
    client: NavasanClient | None = None, session_factory: async_sessionmaker | None = None,
) -> list[AssetQuote]:
    """قیمت لحظه‌ای همه دارایی‌ها را می‌گیرد و به‌عنوان snapshot امروز ذخیره می‌کند."""
    owns_client = client is None
    client = client or NavasanClient()
    factory = session_factory or get_session_factory()
    try:
        quotes, dropped = parse_quotes(await client.latest())
        if not quotes:
            raise TSETMCError("هیچ دارایی‌ای از نوسان پارس نشد")
        log.info("assets_fetched", count=len(quotes), dropped=dropped)

        today = datetime.now(UTC).date()
        async with factory() as session:
            for q in quotes:
                stmt = insert(AssetSnapshotRow).values(
                    key=q.key, trade_date=today, value=q.value, change=q.change,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=["key", "trade_date"],
                    set_={"value": q.value, "change": q.change},
                )
                await session.execute(stmt)
            await session.commit()
        return quotes
    finally:
        if owns_client:
            await client.aclose()


async def get_asset_history(
    key: str, session_factory: async_sessionmaker | None = None,
) -> list[AssetHistoryPoint]:
    factory = session_factory or get_session_factory()
    async with factory() as session:
        q = (
            select(AssetSnapshotRow)
            .where(AssetSnapshotRow.key == key)
            .order_by(AssetSnapshotRow.trade_date)
        )
        rows = (await session.execute(q)).scalars().all()
        return [AssetHistoryPoint(trade_date=r.trade_date, value=r.value) for r in rows]