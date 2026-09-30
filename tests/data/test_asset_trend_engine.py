# tests/engines/test_asset_trend_engine.py
from datetime import date, timedelta

import pytest

from market_analyst.data.assets.models import AssetHistoryPoint
from market_analyst.engines.asset_trend.engine import AssetTrendEngine

engine = AssetTrendEngine()


def _history(values: list[float]) -> list[AssetHistoryPoint]:
    start = date(2024, 1, 1)
    return [AssetHistoryPoint(trade_date=start + timedelta(days=i), value=v) for i, v in enumerate(values)]


def test_single_point_gives_unknown_trend():
    result = engine.analyze("usd_sell", _history([580000]))
    assert result.trend == "unknown"
    assert result.change_pct_1d is None


def test_rising_values_give_up_trend():
    result = engine.analyze("usd_sell", _history([580000, 585000]))
    assert result.trend == "up"
    assert result.change_pct_1d > 0


def test_empty_history_raises():
    with pytest.raises(ValueError):
        engine.analyze("usd_sell", [])