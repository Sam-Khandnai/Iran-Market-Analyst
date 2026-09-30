from datetime import date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class InstrumentRow(Base):
    __tablename__ = "instruments"

    ins_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(200))
    isin: Mapped[str | None] = mapped_column(String(20))
    sector_code: Mapped[str | None] = mapped_column(String(10))
    sector_name: Mapped[str | None] = mapped_column(String(100))
    shares_outstanding: Mapped[int | None] = mapped_column(BigInteger)
    base_volume: Mapped[int | None] = mapped_column(BigInteger)
    eps: Mapped[float | None] = mapped_column(Float)
    sector_pe: Mapped[float | None] = mapped_column(Float)
    market_flow: Mapped[int | None] = mapped_column(Integer)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DailyPriceRow(Base):
    __tablename__ = "daily_prices"

    ins_code: Mapped[str] = mapped_column(
        ForeignKey("instruments.ins_code", ondelete="CASCADE"), primary_key=True
    )
    trade_date: Mapped[date] = mapped_column(Date, primary_key=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    last: Mapped[float] = mapped_column(Float)
    yesterday: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(BigInteger)
    value: Mapped[int] = mapped_column(BigInteger)
    trades: Mapped[int] = mapped_column(Integer)




class DocumentChunkRow(Base):
    __tablename__ = "document_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_doc_chunk"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chunk_id: Mapped[str] = mapped_column(String(300), index=True)
    document_id: Mapped[str] = mapped_column(String(200), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    doc_type: Mapped[str] = mapped_column(String(30), index=True)
    source: Mapped[str] = mapped_column(String(200))
    symbol: Mapped[str | None] = mapped_column(String(64), index=True)
    title: Mapped[str | None] = mapped_column(String(300))
    published_at: Mapped[Date | None] = mapped_column(Date)
    text: Mapped[str] = mapped_column(String(4000))
    embedding: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AssetSnapshotRow(Base):
    __tablename__ = "asset_snapshots"
    __table_args__ = (UniqueConstraint("key", "trade_date", name="uq_asset_snapshot"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), index=True)
    trade_date: Mapped[Date] = mapped_column(Date)
    value: Mapped[float] = mapped_column(Float)
    change: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())