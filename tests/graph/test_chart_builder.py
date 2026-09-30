from market_analyst.graph.chart_builder import build_chart_series
from tests.engines.conftest import make_prices


def test_empty_prices_returns_empty_list():
    assert build_chart_series([]) == []


def test_series_has_expected_keys_and_length():
    prices = make_prices([1000 + i for i in range(200)])
    series = build_chart_series(prices, lookback=90)
    assert len(series) == 90
    assert set(series[0].keys()) == {"date", "close", "sma20", "sma50", "volume"}


def test_dates_are_in_ascending_order():
    prices = make_prices([1000 + i for i in range(150)])
    series = build_chart_series(prices)
    dates = [s["date"] for s in series]
    assert dates == sorted(dates)


def test_sma_null_during_warmup_then_populated():
    prices = make_prices([1000] * 100)
    series = build_chart_series(prices, lookback=100)
    assert series[0]["sma50"] is None  # هنوز به ۵۰ روز نرسیده
    assert series[-1]["sma50"] is not None