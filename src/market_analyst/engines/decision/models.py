from datetime import date

from pydantic import BaseModel, Field

from market_analyst.engines.fundamental.models import FundamentalResult
from market_analyst.engines.market_context.models import MarketContextResult
from market_analyst.engines.risk.models import RiskResult
from market_analyst.engines.technical.models import TechnicalResult
from market_analyst.schemas.report import Signal


class DecisionInput(BaseModel):
    symbol: str
    as_of: date

    technical: TechnicalResult | None = None
    fundamental: FundamentalResult | None = None
    market_context: MarketContextResult | None = None
    risk: RiskResult | None = None


class DecisionResult(BaseModel):
    symbol: str
    as_of: date

    signal: Signal
    confidence: float = Field(..., ge=0, le=1)
    composite_score: float = Field(..., ge=0, le=100)
    component_scores: dict[str, float | None]

    agreement_ratio: float = Field(..., ge=0, le=1)
    conflicts: list[str]
    key_factors: list[str]
    risks: list[str]

    missing_inputs: list[str]
    coverage: float = Field(..., ge=0, le=1)