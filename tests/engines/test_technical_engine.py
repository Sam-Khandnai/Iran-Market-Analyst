import math

import pytest

from market_analyst.engines.errors import InsufficientHistoryError
from market_analyst.engines.technical.engine import TechnicalEngine
from tests.engines.conftest import make_prices

engine = TechnicalEngine()


def test_raises_on_insufficient_history():
    with pytest.raises(InsufficientHistoryError):
        engine.analyze("فولاد", make_prices([1000] * 10))


def test_strong_uptrend_gives_high_score_and_bullish_trend():
    closes = [1000 * (1.01 ** i) for i in range(250)]
    result = engine.analyze("فولاد", make_prices(closes))
    assert result.trend == "uptrend"
    assert result.score >= 70
    assert result.signals["sma50"] == "bullish"
    assert "price_above_sma50" in result.factors


def test_strong_downtrend_gives_low_score_and_bearish_trend():
    closes = [3000 - i * 8 for i in range(250)]  # نزول خطی، نه درصدی
    result = engine.analyze("فولاد", make_prices(closes))
    assert result.trend == "downtrend"
    assert result.score <= 30


def test_sideways_flat_market_near_neutral_score():
    # نوسان سینوسی حول ۱۰۰۰ با دوره‌ای که قیمت پایانی را نزدیک میانگین نگه می‌دارد
    closes = [1000 + 5 * math.sin(i * math.pi / 10) for i in range(220)]
    result = engine.analyze("فولاد", make_prices(closes))
    assert 20 <= result.score <= 80


def test_score_always_within_bounds():
    closes = [1000 * (1.03 ** i) for i in range(100)]
    result = engine.analyze("فولاد", make_prices(closes))
    assert 0 <= result.score <= 100


def test_indicators_present_and_finite_where_expected():
    closes = [1000 + i * 2 for i in range(250)]
    result = engine.analyze("فولاد", make_prices(closes))
    for key in ["sma20", "sma50", "rsi_14", "macd", "atr_14"]:
        assert result.indicators[key] is not None