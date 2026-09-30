from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from market_analyst.data.db.tables import DailyPriceRow, InstrumentRow
from market_analyst.data.models import DailyPrice, Instrument

_CHUNK = 1000  # محدودیت تعداد پارامتر asyncpg


class Repository:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def upsert_instrument(self, inst: Instrument) -> None:
        values = inst.model_dump()
        stmt = insert(InstrumentRow).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ins_code"],
            set_={k: v for k, v in values.items() if k != "ins_code"}
            | {"updated_at": datetime.now().astimezone()},
        )
        await self.s.execute(stmt)

    async def upsert_prices(self, prices: list[DailyPrice]) -> None:
        for i in range(0, len(prices), _CHUNK):
            rows = [p.model_dump() for p in prices[i : i + _CHUNK]]
            stmt = insert(DailyPriceRow).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["ins_code", "trade_date"],
                set_={c: stmt.excluded[c] for c in rows[0] if c not in ("ins_code", "trade_date")},
            )
            await self.s.execute(stmt)

    async def get_instrument_by_symbol(self, symbol: str) -> tuple[Instrument, datetime] | None:
        q = (
            select(InstrumentRow)
            .where(InstrumentRow.symbol == symbol)
            .order_by(InstrumentRow.updated_at.desc())
            .limit(1)
        )
        row = (await self.s.execute(q)).scalar_one_or_none()
        if row is None:
            return None
        inst = Instrument(**{c: getattr(row, c) for c in Instrument.model_fields})
        return inst, row.updated_at

    async def get_prices(self, ins_code: str) -> list[DailyPrice]:
        q = (
            select(DailyPriceRow)
            .where(DailyPriceRow.ins_code == ins_code)
            .order_by(DailyPriceRow.trade_date)
        )
        rows = (await self.s.execute(q)).scalars().all()
        return [DailyPrice(**{c: getattr(r, c) for c in DailyPrice.model_fields}) for r in rows]