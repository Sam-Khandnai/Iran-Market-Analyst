from datetime import date

from market_analyst.engines.decision.engine import DecisionEngine
from market_analyst.engines.decision.models import DecisionInput
from market_analyst.engines.fundamental.models import FundamentalResult
from market_analyst.engines.market_context.models import MarketContextResult
from market_analyst.engines.risk.models import RiskResult
from market_analyst.engines.technical.models import TechnicalResult
from market_analyst.schemas.report import Signal

engine = DecisionEngine()
D = date(2024, 1, 1)


def _technical(score=85, trend="uptrend", data_points=250, factors=None) -> TechnicalResult:
    return TechnicalResult(
        symbol="فولاد", as_of=D, price=1000, indicators={},
        signals={}, score=score, trend=trend, factors=factors or ["price_above_sma50"],
        data_points=data_points,
    )


def _fundamental(score=85, coverage=1.0, factors=None) -> FundamentalResult:
    return FundamentalResult(
        symbol="فولاد", as_of=D, metrics={}, signals={}, score=score,
        factors=factors or ["strong_growth"], missing_inputs=[], coverage=coverage,
    )


def _market_context(score=85, coverage=1.0, factors=None) -> MarketContextResult:
    return MarketContextResult(
        symbol="فولاد", as_of=D, metrics={}, signals={}, score=score,
        market_regime="risk_on", factors=factors or ["market_uptrend"],
        missing_inputs=[], coverage=coverage,
    )


def _risk(risk_score=15, risk_level="low", coverage=1.0, factors=None) -> RiskResult:
    return RiskResult(
        symbol="فولاد", as_of=D, metrics={}, risk_factors={},
        risk_score=risk_score, risk_level=risk_level,
        contributing_factors=factors or ["low_volatility"],
        missing_inputs=[], coverage=coverage,
    )


def test_all_strong_bullish_low_risk_gives_strong_positive_high_confidence():
    data = DecisionInput(
        symbol="فولاد", as_of=D,
        technical=_technical(90), fundamental=_fundamental(88),
        market_context=_market_context(85), risk=_risk(10, "low"),
    )
    result = engine.analyze(data)
    assert result.signal == Signal.STRONG_POSITIVE
    assert result.confidence >= 0.8
    assert result.conflicts == []
    assert result.coverage == 1.0


def test_all_strong_bearish_high_risk_gives_strong_negative():
    data = DecisionInput(
        symbol="فولاد", as_of=D,
        technical=_technical(10, trend="downtrend"), fundamental=_fundamental(12),
        market_context=_market_context(8), risk=_risk(90, "high"),
    )
    result = engine.analyze(data)
    assert result.signal == Signal.STRONG_NEGATIVE  # already floor, downgrade has no effect


def test_high_risk_downgrades_signal_by_one_level():
    data = DecisionInput(
        symbol="فولاد", as_of=D,
        technical=_technical(90), fundamental=_fundamental(88),
        market_context=_market_context(85), risk=_risk(80, "high"),
    )
    result = engine.analyze(data)
    # امتیاز ترکیبی هنوز بالاست ولی باید یک پله تنزل کند
    assert result.signal in (Signal.POSITIVE, Signal.WATCH)
    assert result.component_scores["risk_adjusted"] == 20.0


def test_conflicting_signals_reduce_confidence_and_are_reported():
    data = DecisionInput(
        symbol="فولاد", as_of=D,
        technical=_technical(90),                 # bullish
        fundamental=_fundamental(15),              # bearish
        market_context=_market_context(85),        # bullish
        risk=_risk(20, "low"),
    )
    result = engine.analyze(data)
    assert result.agreement_ratio < 1.0
    assert any("technical_bullish_vs_fundamental_bearish" in c for c in result.conflicts)


def test_missing_engines_reduce_coverage_and_are_listed():
    data = DecisionInput(symbol="فولاد", as_of=D, technical=_technical(90))
    result = engine.analyze(data)
    assert 0 < result.coverage < 1.0
    assert set(result.missing_inputs) == {"fundamental", "market_context", "risk"}


def test_no_inputs_gives_watch_zero_confidence():
    data = DecisionInput(symbol="فولاد", as_of=D)
    result = engine.analyze(data)
    assert result.signal == Signal.WATCH  
    assert result.confidence == 0.0
    assert result.coverage == 0.0


def test_mid_range_scores_give_watch_signal():
    data = DecisionInput(
        symbol="فولاد", as_of=D,
        technical=_technical(72), fundamental=_fundamental(61),
        market_context=_market_context(55), risk=_risk(30, "medium"),
    )
    result = engine.analyze(data)
    assert result.signal in (Signal.WATCH, Signal.POSITIVE)


def test_composite_score_and_confidence_always_within_bounds():
    data = DecisionInput(
        symbol="فولاد", as_of=D,
        technical=_technical(100), fundamental=_fundamental(0),
        market_context=_market_context(100), risk=_risk(0, "low"),
    )
    result = engine.analyze(data)
    assert 0 <= result.composite_score <= 100
    assert 0 <= result.confidence <= 1