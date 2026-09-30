import pandas as pd

from market_analyst.data.models import DailyPrice
from market_analyst.engines.technical.adjust import adjust_prices
from market_analyst.engines.technical.indicators import sma


def build_chart_series(prices: list[DailyPrice], lookback: int = 90) -> list[dict]:
    """سری قیمت تعدیل‌شده + SMA20/50 برای آخرین `lookback` روز، برای نمایش نمودار در Frontend."""
    if not prices:
        return []

    df = adjust_prices(prices)
    df["sma20"] = sma(df["adj_close"], 20)
    df["sma50"] = sma(df["adj_close"], 50)
    tail = df.tail(lookback)

    out: list[dict] = []
    for _, row in tail.iterrows():
        out.append({
            "date": row["trade_date"].isoformat(),
            "close": round(float(row["adj_close"]), 2),
            "sma20": None if pd.isna(row["sma20"]) else round(float(row["sma20"]), 2),
            "sma50": None if pd.isna(row["sma50"]) else round(float(row["sma50"]), 2),
            "volume": int(row["volume"]),
        })
    return out