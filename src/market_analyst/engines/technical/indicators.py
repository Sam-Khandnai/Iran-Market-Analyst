import numpy as np
import pandas as pd


def sma(s: pd.Series, window: int) -> pd.Series:
    return s.rolling(window).mean()


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def rsi(s: pd.Series, period: int = 14) -> pd.Series:
    delta = s.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.where(avg_loss != 0, 100.0)  # zero loss => RSI=100


def macd(
    s: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast, ema_slow = ema(s, fast), ema(s, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    return macd_line, signal_line, macd_line - signal_line


def bollinger(
    s: pd.Series, window: int = 20, num_std: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = sma(s, window)
    std = s.rolling(window).std()
    return mid + num_std * std, mid, mid - num_std * std


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["adj_high"], df["adj_low"], df["adj_close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def stochastic(
    df: pd.DataFrame, k_period: int = 14, d_period: int = 3
) -> tuple[pd.Series, pd.Series]:
    low_min = df["adj_low"].rolling(k_period).min()
    high_max = df["adj_high"].rolling(k_period).max()
    denom = (high_max - low_min).replace(0, np.nan)
    k = 100 * (df["adj_close"] - low_min) / denom
    return k, k.rolling(d_period).mean()


def obv(df: pd.DataFrame) -> pd.Series:
    direction = np.sign(df["adj_close"].diff()).fillna(0)
    return (direction * df["volume"]).cumsum()