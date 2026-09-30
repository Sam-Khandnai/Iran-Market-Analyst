import numpy as np
import pandas as pd

from market_analyst.data.models import DailyPrice


def adjust_prices(prices: list[DailyPrice], tolerance: float = 0.005) -> pd.DataFrame:
    """تعدیل قهقرایی (back-adjustment) برای افزایش سرمایه/DPS.

    منطق: قیمت پایانی دیروز طبق TSETMC در روز t (`yesterday`) باید برابر
    close روز t-1 باشد. اگر اختلاف بیش از tolerance بود، یعنی رویداد شرکتی
    رخ داده و تمام روزهای قبل از t با نسبت yesterday[t]/close[t-1] ضرب می‌شوند.
    """
    df = (
        pd.DataFrame([p.model_dump() for p in prices])
        .sort_values("trade_date")
        .reset_index(drop=True)
    )
    n = len(df)
    factors = np.ones(n)
    cum = 1.0
    for i in range(n - 1, 0, -1):
        prev_close = df.loc[i - 1, "close"]
        ref_yesterday = df.loc[i, "yesterday"]
        if prev_close > 0:
            ratio = ref_yesterday / prev_close
            if abs(ratio - 1.0) > tolerance:
                cum *= ratio
        factors[i - 1] = cum

    df["adj_factor"] = factors
    for col in ("open", "high", "low", "close", "last"):
        df[f"adj_{col}"] = df[col] * df["adj_factor"]
    return df