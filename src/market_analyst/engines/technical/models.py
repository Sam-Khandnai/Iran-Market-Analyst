from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

Signal = Literal["bullish", "bearish", "neutral"]


class TechnicalResult(BaseModel):
    symbol: str
    as_of: date
    price: float
    indicators: dict[str, float | None]
    signals: dict[str, Signal]
    score: float = Field(..., ge=0, le=100)
    trend: Literal["uptrend", "downtrend", "sideways"]
    factors: list[str]
    data_points: int