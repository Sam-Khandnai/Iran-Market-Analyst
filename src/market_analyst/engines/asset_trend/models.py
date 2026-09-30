# models.py
from datetime import date
from typing import Literal

from pydantic import BaseModel

Trend = Literal["up", "down", "flat", "unknown"]


class AssetTrendResult(BaseModel):
    key: str
    as_of: date
    current_value: float
    change_1d: float | None = None
    change_pct_1d: float | None = None
    change_pct_7d: float | None = None
    change_pct_30d: float | None = None
    trend: Trend
    data_points: int