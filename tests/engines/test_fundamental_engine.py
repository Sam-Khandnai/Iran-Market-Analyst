from datetime import date

from market_analyst.engines.fundamental.engine import FundamentalEngine
from market_analyst.engines.fundamental.models import FundamentalInput

engine = FundamentalEngine()


def _base(**overrides) -> FundamentalInput:
    defaults = {
        "symbol": "فولاد", "as_of": date(2024, 1, 1),
        "price": 1000, "eps": 150, "sector_pe": 10,
        "book_value_per_share": 900,
        "revenue_ttm": 1200, "revenue_ttm_prev_year": 1000,
        "net_income_ttm": 180, "net_income_ttm_prev_year": 150,
        "operating_margin": 0.20, "net_margin": 0.18,
        "debt_to_equity": 0.4, "current_ratio": 1.8, "roe": 0.22,
        "dividend_per_share_ttm": 50,
    }
    defaults.update(overrides)
    return FundamentalInput(**defaults)


def test_strong_fundamentals_give_high_score():
    result = engine.analyze(_base())
    assert result.score >= 75
    assert result.signals["pe"] == "bullish"
    assert result.coverage == 1.0
    assert result.missing_inputs == []


def test_weak_fundamentals_give_low_score():
    data = _base(
        price=3000,
        book_value_per_share=500,
        revenue_ttm=900, revenue_ttm_prev_year=1000,
        net_income_ttm=90, net_income_ttm_prev_year=150,
        net_margin=0.02, operating_margin=0.03,
        debt_to_equity=2.0, current_ratio=0.7, roe=0.05,
    )
    result = engine.analyze(data)
    assert result.score <= 30
    assert result.signals["leverage"] == "bearish"
    assert "high_leverage" in result.factors


def test_pe_not_computed_when_eps_negative_or_zero():
    result = engine.analyze(_base(eps=-5))
    assert result.metrics["pe"] is None
    assert "pe" not in result.signals


def test_missing_fields_reduce_coverage_but_do_not_crash():
    result = engine.analyze(_base(
        book_value_per_share=None, debt_to_equity=None, current_ratio=None,
    ))
    assert 0 < result.coverage < 1.0
    assert "book_value_per_share" in result.missing_inputs
    assert "pb" not in result.signals


def test_all_fields_missing_gives_neutral_score_zero_coverage():
    data = FundamentalInput(symbol="X", as_of=date(2024, 1, 1), price=1000)
    result = engine.analyze(data)
    assert result.score == 50.0
    assert result.coverage == 0.0
    assert result.signals == {}


def test_score_always_within_bounds():
    result = engine.analyze(_base(price=10_000_000, eps=1))
    assert 0 <= result.score <= 100


def test_dividend_yield_computed_correctly():
    result = engine.analyze(_base(price=1000, dividend_per_share_ttm=50))
    assert result.metrics["dividend_yield"] == 0.05
