import numpy as np

from market_analyst.data.models import DailyPrice
from market_analyst.engines.errors import InsufficientHistoryError
from market_analyst.engines.technical.adjust import adjust_prices
from market_analyst.engines.technical.indicators import (
    atr,
    bollinger,
    ema,
    macd,
    obv,
    rsi,
    sma,
    stochastic,
)
from market_analyst.engines.technical.models import Signal, TechnicalResult

MIN_ROWS = 30


def _f(x) -> float | None:
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 4)


class TechnicalEngine:
    def analyze(self, symbol: str, prices: list[DailyPrice]) -> TechnicalResult:
        if len(prices) < MIN_ROWS:
            raise InsufficientHistoryError(len(prices), MIN_ROWS)

        df = adjust_prices(prices)
        close = df["adj_close"]

        sma20, sma50, sma200 = sma(close, 20), sma(close, 50), sma(close, 200)
        ema12, ema26 = ema(close, 12), ema(close, 26)
        rsi14 = rsi(close, 14)
        macd_line, macd_signal, macd_hist = macd(close)
        bb_up, bb_mid, bb_low = bollinger(close, 20, 2.0)
        atr14 = atr(df, 14)
        stoch_k, stoch_d = stochastic(df, 14, 3)
        obv_s = obv(df)
        vol_sma20 = sma(df["volume"], 20)

        last = -1
        price = float(df["close"].iloc[last])
        c = float(close.iloc[last])
        r = rsi14.iloc[last]
        ml, msig = macd_line.iloc[last], macd_signal.iloc[last]
        s50, s200 = sma50.iloc[last], sma200.iloc[last]
        bu, bl = bb_up.iloc[last], bb_low.iloc[last]
        vol, vsma = df["volume"].iloc[last], vol_sma20.iloc[last]

        score = 50.0
        factors: list[str] = []
        signals: dict[str, Signal] = {}

        def bump(points: float, code: str) -> None:
            nonlocal score
            score += points
            factors.append(code)

        # SMA50
        if not np.isnan(s50):
            if c > s50:
                bump(10, "price_above_sma50"); signals["sma50"] = "bullish"
            else:
                bump(-10, "price_below_sma50"); signals["sma50"] = "bearish"

        # SMA200 + روند
        if not np.isnan(s200):
            if c > s200:
                bump(10, "price_above_sma200"); signals["sma200"] = "bullish"
            else:
                bump(-10, "price_below_sma200"); signals["sma200"] = "bearish"

        if not np.isnan(s50) and not np.isnan(s200):
            if c > s50 > s200:
                trend = "uptrend"
            elif c < s50 < s200:
                trend = "downtrend"
            else:
                trend = "sideways"
        else:
            trend = "sideways"

        # RSI
        if not np.isnan(r):
            if r >= 70:
                bump(-5, "rsi_overbought"); signals["rsi"] = "bearish"
            elif r <= 30:
                bump(5, "rsi_oversold"); signals["rsi"] = "bullish"
            elif r >= 55:
                bump(8, "rsi_bullish_momentum"); signals["rsi"] = "bullish"
            elif r <= 45:
                bump(-8, "rsi_bearish_momentum"); signals["rsi"] = "bearish"
            else:
                signals["rsi"] = "neutral"

        # MACD
        if not np.isnan(ml) and not np.isnan(msig):
            if ml > msig:
                bump(10, "macd_bullish_cross"); signals["macd"] = "bullish"
            else:
                bump(-10, "macd_bearish_cross"); signals["macd"] = "bearish"

        # Bollinger
        if not np.isnan(bu) and not np.isnan(bl):
            if c <= bl:
                bump(5, "bb_near_lower_band"); signals["bollinger"] = "bullish"
            elif c >= bu:
                bump(-5, "bb_near_upper_band"); signals["bollinger"] = "bearish"
            else:
                signals["bollinger"] = "neutral"

        # حجم
        if not np.isnan(vsma) and vsma > 0:
            price_up = len(close) > 1 and c > close.iloc[-2]
            if vol > vsma and price_up:
                bump(5, "volume_confirms_up")
            elif vol > vsma and not price_up:
                bump(-5, "volume_confirms_down")

        score = max(0.0, min(100.0, score))

        indicators = {
            "sma20": _f(sma20.iloc[last]), "sma50": _f(s50), "sma200": _f(s200),
            "ema12": _f(ema12.iloc[last]), "ema26": _f(ema26.iloc[last]),
            "rsi_14": _f(r),
            "macd": _f(ml), "macd_signal": _f(msig), "macd_hist": _f(macd_hist.iloc[last]),
            "bb_upper": _f(bu), "bb_mid": _f(bb_mid.iloc[last]), "bb_lower": _f(bl),
            "atr_14": _f(atr14.iloc[last]),
            "stoch_k": _f(stoch_k.iloc[last]), "stoch_d": _f(stoch_d.iloc[last]),
            "obv": _f(obv_s.iloc[last]),
            "volume_sma20": _f(vsma),
        }

        return TechnicalResult(
            symbol=symbol,
            as_of=df["trade_date"].iloc[last],
            price=price,
            indicators=indicators,
            signals=signals,
            score=round(score, 2),
            trend=trend,
            factors=factors,
            data_points=len(prices),
        )