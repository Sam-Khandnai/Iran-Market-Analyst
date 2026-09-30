from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Signal = Literal["bullish", "bearish", "neutral"]


class MarketContextInput(BaseModel):
    symbol: str
    as_of: date

    market_index_change_1d: float | None = None
    market_index_change_1m: float | None = None
    market_breadth: float | None = None

    sector_index_change_1d: float | None = None
    sector_index_change_1m: float | None = None
    sector_rank: int | None = None
    total_sectors: int | None = None

    symbol_return_1m: float | None = None
    symbol_return_3m: float | None = None

    real_money_net_ratio: float | None = None
    volume_relative_to_avg: float | None = None
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
