from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Signal = Literal["bullish", "bearish", "neutral"]


class FundamentalInput(BaseModel):
    """ورودی استاندارد Engine. فیلدهای اختیاری چون همیشه همه داده در دسترس نیست."""

    symbol: str
    as_of: date

    price: float = Field(..., gt=0)
    eps: float | None = None                 # سود هر سهم (TTM یا برآوردی)
    sector_pe: float | None = None

    book_value_per_share: float | None = None
    revenue_ttm: float | None = None
    revenue_ttm_prev_year: float | None = None
    net_income_ttm: float | None = None
    net_income_ttm_prev_year: float | None = None
    operating_margin: float | None = None     # 0..1
    net_margin: float | None = None           # 0..1
    debt_to_equity: float | None = None
    current_ratio: float | None = None
    roe: float | None = None                  # 0..1
    dividend_per_share_ttm: float | None = None


class FundamentalResult(BaseModel):
    symbol: str
    as_of: date

    metrics: dict[str, float | None]
    signals: dict[str, Signal]
    score: float = Field(..., ge=0, le=100)
    factors: list[str]
    missing_inputs: list[str]
    coverage: float = Field(..., ge=0, le=1)   # نسبت متریک‌های قابل‌محاسبه