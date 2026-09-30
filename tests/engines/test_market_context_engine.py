from datetime import date

from market_analyst.engines.market_context.engine import MarketContextEngine
from market_analyst.engines.market_context.models import MarketContextInput

engine = MarketContextEngine()


def _base(**overrides) -> MarketContextInput:
    defaults = {
        "symbol": "فولاد", "as_of": date(2024, 1, 1),
        "market_index_change_1d": 0.01, "market_index_change_1m": 0.05,
        "market_breadth": 0.3,
        "sector_index_change_1d": 0.015, "sector_index_change_1m": 0.08,
        "sector_rank": 3, "total_sectors": 40,
        "symbol_return_1m": 0.12, "symbol_return_3m": 0.20,
        "real_money_net_ratio": 0.08,
        "volume_relative_to_avg": 1.5,
        "queue_state": "buy_queue",
    }
    defaults.update(overrides)
    return MarketContextInput(**defaults)


def test_strong_bullish_context_gives_high_score_and_risk_on():
    result = engine.analyze(_base())
    assert result.score >= 80
    assert result.market_regime == "risk_on"
    assert result.signals["symbol_vs_sector"] == "bullish"
    assert result.coverage == 1.0


def test_weak_bearish_context_gives_low_score_and_risk_off():
    data = _base(
        market_index_change_1m=-0.06, market_breadth=-0.3,
        sector_index_change_1m=-0.07, sector_rank=38, total_sectors=40,
        symbol_return_1m=-0.15,
        real_money_net_ratio=-0.10,
        queue_state="sell_queue",
    )
    result = engine.analyze(data)
    assert result.score <= 20
    assert result.market_regime == "risk_off"
    assert "real_money_outflow" in result.factors


def test_symbol_leading_sector_detected():
    result = engine.analyze(_base(symbol_return_1m=0.15, sector_index_change_1m=0.05))
    assert result.metrics["symbol_vs_sector"] == 0.10
    assert result.signals["symbol_vs_sector"] == "bullish"


def test_symbol_lagging_sector_detected():
    result = engine.analyze(_base(symbol_return_1m=0.01, sector_index_change_1m=0.08))
    assert result.signals["symbol_vs_sector"] == "bearish"


def test_sector_percentile_computed_from_rank():
    result = engine.analyze(_base(sector_rank=1, total_sectors=40))
    assert result.metrics["sector_percentile"] == 1.0
    result2 = engine.analyze(_base(sector_rank=40, total_sectors=40))
    assert result2.metrics["sector_percentile"] < 0.05


def test_missing_fields_reduce_coverage_but_do_not_crash():
    result = engine.analyze(_base(
        sector_rank=None, total_sectors=None, real_money_net_ratio=None,
    ))
    assert 0 < result.coverage < 1.0
    assert "real_money_net_ratio" in result.missing_inputs
    assert "money_flow" not in result.signals


def test_all_fields_missing_gives_neutral_score_zero_coverage():
    data = MarketContextInput(symbol="X", as_of=date(2024, 1, 1))
    result = engine.analyze(data)
    assert result.score == 50.0
    assert result.market_regime == "neutral"
    assert result.coverage == 0.0


def test_no_queue_is_neutral_not_missing():
    result = engine.analyze(_base(queue_state="none"))
    assert result.signals["queue"] == "neutral"
    assert "queue" not in result.missing_inputs  # queue_state جزو required نیست


def test_score_always_within_bounds():
    result = engine.analyze(_base(market_index_change_1m=5.0, sector_index_change_1m=5.0))
    assert 0 <= result.score <= 100