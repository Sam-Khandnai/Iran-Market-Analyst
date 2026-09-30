# engine.py
from market_analyst.data.assets.models import AssetHistoryPoint
from market_analyst.engines.asset_trend.models import AssetTrendResult


def _pct(curr: float, past: float | None) -> float | None:
    if past is None or past == 0:
        return None
    return round((curr - past) / past * 100, 2)


class AssetTrendEngine:
    def analyze(self, key: str, history: list[AssetHistoryPoint]) -> AssetTrendResult:
        if not history:
            raise ValueError("تاریخچه خالی است")

        history = sorted(history, key=lambda p: p.trade_date)
        current = history[-1]
        prev_1d = history[-2].value if len(history) >= 2 else None
        prev_7d = history[-8].value if len(history) >= 8 else None
        prev_30d = history[-31].value if len(history) >= 31 else None

        change_1d = None if prev_1d is None else round(current.value - prev_1d, 2)
        pct_1d = _pct(current.value, prev_1d)

        if pct_1d is None:
            trend = "unknown"
        elif pct_1d > 0.3:
            trend = "up"
        elif pct_1d < -0.3:
            trend = "down"
        else:
            trend = "flat"

        return AssetTrendResult(
            key=key, as_of=current.trade_date, current_value=current.value,
            change_1d=change_1d, change_pct_1d=pct_1d,
            change_pct_7d=_pct(current.value, prev_7d),
            change_pct_30d=_pct(current.value, prev_30d),
            trend=trend, data_points=len(history),
        )