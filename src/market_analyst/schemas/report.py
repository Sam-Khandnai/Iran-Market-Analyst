from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Signal(str, Enum):
    """سیگنال پژوهشی؛ توصیه سرمایه‌گذاری نیست."""

    STRONG_POSITIVE = "STRONG_POSITIVE"
    POSITIVE = "POSITIVE"
    WATCH = "WATCH"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    STRONG_NEGATIVE = "STRONG_NEGATIVE"


class Decision(BaseModel):
    signal: Signal
    confidence: float = Field(..., ge=0.0, le=1.0)


class Evidence(BaseModel):
    source: str          # مثلاً "technical.rsi_14"
    description: str
    value: Any = None


class AnalysisReport(BaseModel):
    symbol: str

    technical_analysis: dict[str, Any] = Field(default_factory=dict)
    fundamental_analysis: dict[str, Any] = Field(default_factory=dict)
    market_context: dict[str, Any] = Field(default_factory=dict)
    news_analysis: dict[str, Any] = Field(default_factory=dict)
    risk_analysis: dict[str, Any] = Field(default_factory=dict)

    decision: Decision | None = None

    key_factors: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    
    chart_data: list[dict[str, Any]] = Field(default_factory=list)
   
    summary: str = ""
    disclaimer: str = (
        "این خروجی صرفاً یک تحلیل پژوهشی مبتنی بر داده است "
        "و توصیه شخصی سرمایه‌گذاری محسوب نمی‌شود."
    )
    generated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )