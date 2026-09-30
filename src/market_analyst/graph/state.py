import operator
from datetime import UTC, date, datetime
from typing import Annotated, TypedDict

from market_analyst.data.models import DailyPrice, Instrument
from market_analyst.engines.decision.models import DecisionResult
from market_analyst.engines.fundamental.models import FundamentalResult
from market_analyst.engines.market_context.models import MarketContextResult
from market_analyst.engines.news.models import NewsResult
from market_analyst.engines.risk.models import RiskResult
from market_analyst.engines.technical.models import TechnicalResult
from market_analyst.schemas.report import AnalysisReport


class GraphState(TypedDict, total=False):
    symbol: str
    timeframe: str
    analysis_period: str

    instrument: Instrument | None
    prices: list[DailyPrice]
    real_money_net_ratio: float | None

    technical: TechnicalResult | None
    fundamental: FundamentalResult | None
    market_context: MarketContextResult | None
    news: NewsResult | None
    risk: RiskResult | None
    decision: DecisionResult | None

    report: AnalysisReport | None
    errors: Annotated[list[str], operator.add]


def as_of_date(state: GraphState) -> date:
    prices = state.get("prices") or []
    return prices[-1].trade_date if prices else datetime.now(UTC).date()