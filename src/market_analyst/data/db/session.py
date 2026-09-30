from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from market_analyst.config import get_settings
from market_analyst.data.db.tables import Base


@lru_cache
def get_engine():
    return create_async_engine(get_settings().database_url, pool_pre_ping=True)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def init_db() -> None:
    """برای فاز توسعه. در Production با Alembic جایگزین می‌شود."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)