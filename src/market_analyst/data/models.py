from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class Instrument(BaseModel):
    ins_code: str
    symbol: str
    name: str
    isin: str | None = None
    sector_code: str | None = None
    sector_name: str | None = None
    shares_outstanding: int | None = None
    base_volume: int | None = None
    eps: float | None = None
    sector_pe: float | None = None
    market_flow: int | None = None


class DailyPrice(BaseModel):
    """یک کندل روزانه خام (تعدیل‌نشده). قیمت‌ها به ریال."""

    ins_code: str
    trade_date: date
    open: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    low: float = Field(..., ge=0)
    close: float = Field(..., gt=0)       # قیمت پایانی (pClosing)
    last: float = Field(..., ge=0)        # آخرین معامله (pDrCotVal)
    yesterday: float = Field(..., ge=0)   # قیمت پایانی دیروز طبق TSETMC
    volume: int = Field(..., ge=0)
    value: int = Field(..., ge=0)
    trades: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _check_range(self):
        if self.high < self.low:
            raise ValueError("high < low")
        return self


class SymbolData(BaseModel):
    instrument: Instrument
    prices: list[DailyPrice]                  # صعودی بر اساس تاریخ
    source: Literal["tsetmc", "cache"]
    stale: bool = False                       # True یعنی TSETMC در دسترس نبود
    dropped_rows: int = 0
    fetched_at: datetime

class ClientTypeSnapshot(BaseModel):
    ins_code: str
    trade_date: date
    buy_individual_volume: int
    buy_legal_volume: int
    buy_individual_count: int
    buy_legal_count: int
    sell_individual_volume: int
    sell_legal_volume: int
    sell_individual_count: int
    sell_legal_count: int