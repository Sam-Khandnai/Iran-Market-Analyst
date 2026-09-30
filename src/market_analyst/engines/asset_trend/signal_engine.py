import statistics

from market_analyst.data.assets.models import AssetHistoryPoint
from market_analyst.engines.asset_trend.models import AssetTrendResult
from market_analyst.schemas.report import Signal

_LEVELS = [
    Signal.STRONG_NEGATIVE, Signal.NEGATIVE, Signal.NEUTRAL,
    Signal.WATCH, Signal.POSITIVE, Signal.STRONG_POSITIVE,
]


def _daily_returns_pct(history: list[AssetHistoryPoint]) -> list[float]:
    vals = [h.value for h in sorted(history, key=lambda p: p.trade_date)]
    out = []
    for i in range(1, len(vals)):
        if vals[i - 1] != 0:
            out.append((vals[i] - vals[i - 1]) / vals[i - 1] * 100)
    return out


def _signal_from_score(score: float) -> Signal:
    if score >= 80:
        return Signal.STRONG_POSITIVE
    if score >= 65:
        return Signal.POSITIVE
    if score >= 50:
        return Signal.WATCH
    if score >= 35:
        return Signal.NEUTRAL
    if score >= 20:
        return Signal.NEGATIVE
    return Signal.STRONG_NEGATIVE


class AssetSignalResult:
    def __init__(
        self, key: str, score: float, signal: Signal, confidence: float,
        volatility_pct: float | None, momentum_pct: float | None, factors: list[str],
    ):
        self.key = key
        self.score = score
        self.signal = signal
        self.confidence = confidence
        self.volatility_pct = volatility_pct
        self.momentum_pct = momentum_pct
        self.factors = factors

    def to_dict(self) -> dict:
        return {
            "key": self.key, "score": self.score, "signal": self.signal.value,
            "confidence": self.confidence, "volatility_pct": self.volatility_pct,
            "momentum_pct": self.momentum_pct, "factors": self.factors,
        }


class AssetSignalEngine:
    """امتیازدهی deterministic بر اساس مومنتوم و نوسان؛ هیچ LLM دخالتی ندارد."""

    def analyze(self, trend: AssetTrendResult, history: list[AssetHistoryPoint]) -> AssetSignalResult:
        components: list[float] = []
        weights: list[float] = []
        factors: list[str] = []

        for pct, weight, label in [
            (trend.change_pct_1d, 1.0, "1d"),
            (trend.change_pct_7d, 2.0, "7d"),
            (trend.change_pct_30d, 1.5, "30d"),
        ]:
            if pct is None:
                continue
            components.append(pct)
            weights.append(weight)
            if pct > 1.0:
                factors.append(f"momentum_positive_{label}")
            elif pct < -1.0:
                factors.append(f"momentum_negative_{label}")

        momentum_pct = (
            sum(c * w for c, w in zip(components, weights, strict=True)) / sum(weights)
            if components else None
        )

        returns = _daily_returns_pct(history)
        volatility_pct = statistics.pstdev(returns) if len(returns) >= 2 else None
        if volatility_pct is not None:
            if volatility_pct > 2.0:
                factors.append("high_volatility")
            elif volatility_pct < 0.5:
                factors.append("low_volatility")

        if momentum_pct is None:
            score = 50.0
        else:
            score = 50.0 + max(-40.0, min(40.0, momentum_pct * 4))
            if volatility_pct is not None and volatility_pct > 2.0:
                score -= min(15.0, (volatility_pct - 2.0) * 5)
        score = max(0.0, min(100.0, round(score, 2)))

        coverage = min(1.0, trend.data_points / 30)
        confidence = coverage
        if volatility_pct is not None and volatility_pct > 2.0:
            confidence *= 0.8
        confidence = round(max(0.0, min(1.0, confidence)), 2)

        return AssetSignalResult(
            key=trend.key, score=score, signal=_signal_from_score(score),
            confidence=confidence, volatility_pct=round(volatility_pct, 3) if volatility_pct else None,
            momentum_pct=round(momentum_pct, 3) if momentum_pct else None, factors=factors,
        )