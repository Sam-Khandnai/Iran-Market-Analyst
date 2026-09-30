from datetime import date

from market_analyst.engines.fundamental.models import FundamentalResult
from market_analyst.engines.market_context.models import MarketContextResult
from market_analyst.engines.risk.engine import RiskEngine
from market_analyst.engines.risk.models import RiskInput
from market_analyst.engines.technical.models import TechnicalResult

engine = RiskEngine()
D = date(2024, 1, 1)


def _technical(**overrides) -> TechnicalResult:
    defaults = {
        "symbol": "فولاد", "as_of": D, "price": 1000,
        "indicators": {"atr_14": 15.0},
        "signals": {}, "score": 60, "trend": "uptrend", "factors": [], "data_points": 250,
    }
    defaults.update(overrides)
    return TechnicalResult(**defaults)


def _fundamental(**overrides) -> FundamentalResult:
    defaults = {
        "symbol": "فولاد", "as_of": D,
        "metrics": {"debt_to_equity": 0.3}, "signals": {}, "score": 70,
        "factors": [], "missing_inputs": [], "coverage": 1.0,
    }
    defaults.update(overrides)
    return FundamentalResult(**defaults)


def _market_context(**overrides) -> MarketContextResult:
    defaults = {
        "symbol": "فولاد", "as_of": D,
        "metrics": {}, "signals": {}, "score": 75, "market_regime": "risk_on",
        "factors": [], "missing_inputs": [], "coverage": 1.0,
    }
    defaults.update(overrides)
    return MarketContextResult(**defaults)


def test_low_risk_profile_gives_low_score_and_level():
    data = RiskInput(
        symbol="فولاد", as_of=D,
        technical=_technical(),
        fundamental=_fundamental(),
        market_context=_market_context(),
        avg_daily_value_rial=80_000_000_000,
        free_float_ratio=0.5,
    )
    result = engine.analyze(data)
    assert result.risk_score <= 20
    assert result.risk_level == "low"
    assert result.risk_factors["volatility"] == "low"
    assert result.coverage == 1.0
    assert result.missing_inputs == []


def test_high_risk_profile_gives_high_score_and_level():
    data = RiskInput(
        symbol="فولاد", as_of=D,
        technical=_technical(
            indicators={"atr_14": 80.0}, price=1000, trend="downtrend", data_points=40,
        ),
        fundamental=_fundamental(metrics={"debt_to_equity": 2.5}, coverage=0.3),
        market_context=_market_context(market_regime="risk_off", coverage=0.2),
        avg_daily_value_rial=1_000_000_000,
        free_float_ratio=0.08,
    )
    result = engine.analyze(data)
    assert result.risk_score >= 70
    assert result.risk_level == "high"
    assert "illiquid_market" in result.contributing_factors
    assert "downtrend_risk" in result.contributing_factors


def test_missing_engines_reduce_coverage_but_do_not_crash():
    data = RiskInput(symbol="فولاد", as_of=D, technical=_technical())
    result = engine.analyze(data)
    assert 0 < result.coverage < 1.0
    assert "fundamental" in result.missing_inputs
    assert "market_context" in result.missing_inputs
    assert "leverage" not in result.risk_factors


def test_no_inputs_at_all_gives_medium_default():
    data = RiskInput(symbol="فولاد", as_of=D)
    result = engine.analyze(data)
    assert result.risk_score == 50.0
    assert result.risk_level == "medium"
    assert result.coverage == 0.0
    assert result.risk_factors == {}


def test_low_data_points_increase_risk_via_data_quality():
    thin = _technical(data_points=40)
    rich = _technical(data_points=250)
    thin_result = engine.analyze(RiskInput(symbol="فولاد", as_of=D, technical=thin))
    rich_result = engine.analyze(RiskInput(symbol="فولاد", as_of=D, technical=rich))
    assert thin_result.risk_score >= rich_result.risk_score


def test_score_always_within_bounds():
    data = RiskInput(
        symbol="فولاد", as_of=D,
        technical=_technical(indicators={"atr_14": 500.0}, price=100),
        avg_daily_value_rial=0,
        free_float_ratio=0.01,
    )
    result = engine.analyze(data)
    assert 0 <= result.risk_score <= 100