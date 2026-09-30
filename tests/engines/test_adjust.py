from market_analyst.engines.technical.adjust import adjust_prices
from tests.engines.conftest import make_prices


def test_no_adjustment_needed_when_flat():
    prices = make_prices([1000, 1010, 1005, 1020, 1030])
    df = adjust_prices(prices)
    assert (df["adj_factor"] == 1.0).all()
    assert list(df["adj_close"]) == list(df["close"])


def test_capital_increase_detected_and_backadjusted():
    prices = make_prices([1000, 1010, 1020])
    # روز بعد: افزایش سرمایه، yesterday نصف close قبلی می‌شود
    prices[-1] = prices[-1].model_copy()
    from market_analyst.data.models import DailyPrice
    corp_action_day = DailyPrice(
        ins_code="X", trade_date=prices[-1].trade_date + __import__("datetime").timedelta(days=1),
        open=520, high=530, low=510, close=525, last=525,
        yesterday=510,  # نصف close روز قبل (1020) تقریباً
        volume=1000, value=525000, trades=50,
    )
    prices.append(corp_action_day)
    df = adjust_prices(prices)

    ratio = 510 / 1020
    assert abs(df["adj_factor"].iloc[-1] - 1.0) < 1e-9
    assert abs(df["adj_factor"].iloc[-2] - ratio) < 1e-9
    assert abs(df["adj_close"].iloc[0] - 1000 * ratio) < 1e-6