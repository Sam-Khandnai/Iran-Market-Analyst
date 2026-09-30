# tests/engines/test_asset_signal_engine.py
from datetime import date, timedelta

from market_analyst.data.assets.models import AssetHistoryPoint
from market_analyst.engines.asset_trend.engine import AssetTrendEngine
from market_analyst.engines.asset_trend.signal_engine import AssetSignalEngine

trend_engine = AssetTrendEngine()
signal_engine = AssetSignalEngine()


def _history(values: list[float]) -> list[AssetHistoryPoint]:
    start = date(2024, 1, 1)
    return [AssetHistoryPoint(trade_date=start + timedelta(days=i), value=v) for i, v in enumerate(values)]


def test_rising_prices_give_positive_signal():
    h = _history([100 * (1.01 ** i) for i in range(35)])
    trend = trend_engine.analyze("usd_sell", h)
    result = signal_engine.analyze(trend, h)
    assert result.score > 50
    assert result.signal.value in ("WATCH", "POSITIVE", "STRONG_POSITIVE")


def test_falling_prices_give_negative_signal():
    h = _history([100 * (0.99 ** i) for i in range(35)])
    trend = trend_engine.analyze("usd_sell", h)
    result = signal_engine.analyze(trend, h)
    assert result.score < 50


def test_short_history_gives_low_confidence():
    h = _history([100, 101])
    trend = trend_engine.analyze("usd_sell", h)
    result = signal_engine.analyze(trend, h)
    assert result.confidence < 0.2


def test_score_always_within_bounds():
    h = _history([100 * (1.5 ** i) for i in range(35)])
    trend = trend_engine.analyze("usd_sell", h)
    result = signal_engine.analyze(trend, h)
    assert 0 <= result.score <= 100