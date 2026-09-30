from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from market_analyst.config import get_settings
from market_analyst.data.db.repository import Repository
from market_analyst.data.db.session import get_session_factory
from market_analyst.data.errors import TSETMCError
from market_analyst.data.models import SymbolData
from market_analyst.data.tsetmc.client import TSETMCClient
from market_analyst.data.tsetmc.parsers import (
    parse_daily_prices,
    parse_instrument,
    parse_search_hits,
    pick_hit,
)
from market_analyst.logging import get_logger
from market_analyst.schemas.request import normalize_persian

log = get_logger("data.service")


async def get_symbol(
    symbol: str,
    *,
    refresh: bool = False,
    client: TSETMCClient | None = None,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> SymbolData:
    settings = get_settings()
    symbol = normalize_persian(symbol)
    factory = session_factory or get_session_factory()
    ttl = timedelta(hours=settings.cache_ttl_hours)
    now = datetime.now(UTC)

    async with factory() as session:
        repo = Repository(session)
        cached = await repo.get_instrument_by_symbol(symbol)

        # ۱) کش تازه
        if cached and not refresh and now - cached[1] < ttl:
            inst = cached[0]
            prices = await repo.get_prices(inst.ins_code)
            if prices:
                return SymbolData(
                    instrument=inst, prices=prices, source="cache", fetched_at=cached[1]
                )

        # ۲) دریافت از TSETMC
        owns_client = client is None
        client = client or TSETMCClient(settings)
        try:
            hit = pick_hit(parse_search_hits(await client.search(symbol)), symbol)
            info = await client.instrument_info(str(hit["insCode"]))
            inst = parse_instrument(hit, info)
            prices, dropped = parse_daily_prices(
                await client.daily_prices(inst.ins_code), inst.ins_code
            )
            if not prices:
                raise TSETMCError(f"تاریخچه قیمت برای {symbol} خالی است")

            await repo.upsert_instrument(inst)
            await repo.upsert_prices(prices)
            await session.commit()
            log.info("symbol_fetched", symbol=symbol, rows=len(prices), dropped=dropped)
            return SymbolData(
                instrument=inst, prices=prices, source="tsetmc",
                dropped_rows=dropped, fetched_at=now,
            )
        except TSETMCError as e:
            # ۳) fallback: کش قدیمی با پرچم stale
            if cached:
                prices = await repo.get_prices(cached[0].ins_code)
                if prices:
                    log.warning("serving_stale", symbol=symbol, error=str(e))
                    return SymbolData(
                        instrument=cached[0], prices=prices, source="cache",
                        stale=True, fetched_at=cached[1],
                    )
            raise
        finally:
            if owns_client:
                await client.aclose()