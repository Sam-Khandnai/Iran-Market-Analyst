import numpy as np
import pandas as pd

from market_analyst.engines.technical.indicators import ema, macd, rsi, sma


def test_sma_matches_manual_average():
    s = pd.Series([1, 2, 3, 4, 5], dtype=float)
    out = sma(s, 3)
    assert np.isnan(out.iloc[1])
    assert out.iloc[2] == 2.0
    assert out.iloc[4] == 4.0


def test_rsi_is_100_for_strictly_increasing_series():
    s = pd.Series(range(1, 40), dtype=float)
    out = rsi(s, 14)
    assert out.iloc[-1] > 99.0


def test_rsi_is_0_for_strictly_decreasing_series():
    s = pd.Series(range(40, 1, -1), dtype=float)
    out = rsi(s, 14)
    assert out.iloc[-1] < 1.0


def test_rsi_bounded_0_100_on_noisy_series():
    rng = np.random.default_rng(42)
    s = pd.Series(100 + np.cumsum(rng.normal(0, 1, 200)))
    out = rsi(s, 14).dropna()
    assert out.between(0, 100).all()


def test_macd_histogram_positive_in_strong_uptrend():
    s = pd.Series(np.linspace(100, 200, 80))
    _, _, hist = macd(s)
    assert hist.iloc[-1] > 0


def test_ema_reacts_faster_than_sma_to_recent_shock():
    s = pd.Series([100.0] * 30 + [200.0] * 5)
    e = ema(s, 10).iloc[-1]
    m = sma(s, 10).iloc[-1]
    assert e > m