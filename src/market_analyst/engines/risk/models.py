from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from market_analyst.engines.fundamental.models import FundamentalResult
from market_analyst.engines.market_context.models import MarketContextResult
from market_analyst.engines.technical.models import TechnicalResult

RiskSignal = Literal["low", "medium", "high"]


class RiskInput(BaseModel):
    symbol: str
    as_of: date

    technical: TechnicalResult | None = None
    fundamental: FundamentalResult | None = None
    market_context: MarketContextResult | None = None

    # فیلدهای خام که در نتایج فازهای قبل نیستند
    avg_daily_value_rial: float | None = None   # میانگین ارزش معاملات روزانه (نقدشوندگی مطلق)
    free_float_ratio: float | None = None        # سهام شناور آزاد، 0..1


class RiskResult(BaseModel):
    symbol: str
    as_of: date

    metrics: dict[str, float | str | None]
    risk_factors: dict[str, RiskSignal]
    risk_score: float = Field(..., ge=0, le=100)   # بالاتر = ریسک بیشتر
    risk_level: Literal["low", "medium", "high"]
    contributing_factors: list[str]
    missing_inputs: list[str]
    coverage: float = Field(..., ge=0, le=1)