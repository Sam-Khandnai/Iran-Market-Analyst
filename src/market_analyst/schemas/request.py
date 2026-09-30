import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Timeframe(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class AnalysisPeriod(str, Enum):
    M3 = "3m"
    M6 = "6m"
    Y1 = "1y"
    Y2 = "2y"


def normalize_persian(text: str) -> str:
    """یکسان‌سازی ی/ک عربی و فارسی و حذف فاصله‌های اضافی."""
    text = text.replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"\s+", " ", text).strip()


class AnalysisRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=40)
    timeframe: Timeframe = Timeframe.DAILY
    analysis_period: AnalysisPeriod = AnalysisPeriod.Y1

    @field_validator("symbol")
    @classmethod
    def _normalize_symbol(cls, v: str) -> str:
        v = normalize_persian(v)
        if not v:
            raise ValueError("symbol نمی‌تواند خالی باشد")
        return v