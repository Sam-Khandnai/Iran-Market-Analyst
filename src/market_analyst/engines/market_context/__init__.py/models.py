from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Signal = Literal["bullish", "bearish", "neutral"]


class MarketContextInput(BaseModel):
    symbol: str
    as_of: date

    # سطح کل بازار (شاخص کل)
    market_index_change_1d: float | None = None   # درصد، مثلاً 0.012 = +1.2%
    market_index_change_1m: float | None = None
    market_breadth: float | None = None            # (تعداد مثبت - منفی) / کل نمادها، در [-1, 1]

    # سطح صنعت
    sector_index_change_1d: float | None = None
    sector_index_change_1m: float | None = None
    sector_rank: int | None = None                  # رتبه صنعت از نظر بازدهی
    total_sectors: int | None = None

    # سطح نماد نسبت به بالادست‌ها
    symbol_return_1m: float | None = None
    symbol_return_3m: float | None = None

    # جریان پول و صف
    real_money_net_ratio: float | None = None       # خالص ورود پول حقیقی / ارزش کل معاملات، در [-1, 1]
    volume_relative_to_avg: float | None = None      # حجم امروز / میانگین حجم، معمولاً 0..5+
    queue_state: Literal["buy_queue", "sell_queue", "none"] | None = None


class MarketContextResult(BaseModel):
    symbol: str
    as_of: date

    metrics: dict[str, float | int | str | None]
    signals: dict[str, Signal]
    score: float = Field(..., ge=0, le=100)
    market_regime: Literal["risk_on", "risk_off", "neutral"]
    factors: list[str]
    missing_inputs: list[str]
    coverage: float = Field(..., ge=0, le=1)