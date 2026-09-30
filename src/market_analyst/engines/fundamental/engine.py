from market_analyst.engines.fundamental.models import (
    FundamentalInput,
    FundamentalResult,
    Signal,
)

# هر متریک با وزن مشخص در امتیاز نهایی سهیم است؛ جمع وزن‌ها = 100
_WEIGHTS = {
    "pe": 20,
    "pb": 10,
    "growth": 15,
    "margin": 15,
    "leverage": 15,
    "liquidity": 10,
    "roe": 15,
}


def _safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return a / b


def _growth(curr: float | None, prev: float | None) -> float | None:
    if curr is None or prev is None or prev == 0:
        return None
    return (curr - prev) / abs(prev)


def _r(x: float | None) -> float | None:
    return None if x is None else round(x, 4)


class FundamentalEngine:
    def analyze(self, data: FundamentalInput) -> FundamentalResult:
        pe = _safe_div(data.price, data.eps) if data.eps and data.eps > 0 else None
        pb = _safe_div(data.price, data.book_value_per_share)
        revenue_growth = _growth(data.revenue_ttm, data.revenue_ttm_prev_year)
        income_growth = _growth(data.net_income_ttm, data.net_income_ttm_prev_year)

        metrics = {
            "pe": _r(pe),
            "pb": _r(pb),
            "sector_pe": _r(data.sector_pe),
            "pe_relative_to_sector": _r(_safe_div(pe, data.sector_pe)),
            "revenue_growth_yoy": _r(revenue_growth),
            "net_income_growth_yoy": _r(income_growth),
            "operating_margin": _r(data.operating_margin),
            "net_margin": _r(data.net_margin),
            "debt_to_equity": _r(data.debt_to_equity),
            "current_ratio": _r(data.current_ratio),
            "roe": _r(data.roe),
            "dividend_yield": _r(_safe_div(data.dividend_per_share_ttm, data.price)),
        }

        signals: dict[str, Signal] = {}
        factors: list[str] = []
        weighted_sum = 0.0
        weighted_total = 0.0

        def score_metric(key: str, weight: int, sub: float | None, sig: Signal, factor: str) -> None:
            nonlocal weighted_sum, weighted_total
            if sub is None:
                return
            weighted_sum += weight * sub
            weighted_total += weight
            signals[key] = sig
            factors.append(factor)

        if pe is not None and data.sector_pe and data.sector_pe > 0:
            rel = pe / data.sector_pe
            if rel < 0.8:
                score_metric("pe", _WEIGHTS["pe"], 1.0, "bullish", "pe_below_sector")
            elif rel > 1.2:
                score_metric("pe", _WEIGHTS["pe"], 0.0, "bearish", "pe_above_sector")
            else:
                score_metric("pe", _WEIGHTS["pe"], 0.5, "neutral", "pe_in_line_with_sector")

        if pb is not None:
            if pb < 1.0:
                score_metric("pb", _WEIGHTS["pb"], 1.0, "bullish", "pb_below_book_value")
            elif pb > 3.0:
                score_metric("pb", _WEIGHTS["pb"], 0.0, "bearish", "pb_high")
            else:
                score_metric("pb", _WEIGHTS["pb"], 0.5, "neutral", "pb_moderate")

        growth_signal = revenue_growth if revenue_growth is not None else income_growth
        if growth_signal is not None:
            if growth_signal > 0.15:
                score_metric("growth", _WEIGHTS["growth"], 1.0, "bullish", "strong_growth")
            elif growth_signal < 0:
                score_metric("growth", _WEIGHTS["growth"], 0.0, "bearish", "negative_growth")
            else:
                score_metric("growth", _WEIGHTS["growth"], 0.5, "neutral", "modest_growth")

        if data.net_margin is not None:
            if data.net_margin > 0.15:
                score_metric("margin", _WEIGHTS["margin"], 1.0, "bullish", "strong_margin")
            elif data.net_margin < 0.03:
                score_metric("margin", _WEIGHTS["margin"], 0.0, "bearish", "weak_margin")
            else:
                score_metric("margin", _WEIGHTS["margin"], 0.5, "neutral", "moderate_margin")

        if data.debt_to_equity is not None:
            if data.debt_to_equity < 0.5:
                score_metric("leverage", _WEIGHTS["leverage"], 1.0, "bullish", "low_leverage")
            elif data.debt_to_equity > 1.5:
                score_metric("leverage", _WEIGHTS["leverage"], 0.0, "bearish", "high_leverage")
            else:
                score_metric("leverage", _WEIGHTS["leverage"], 0.5, "neutral", "moderate_leverage")

        if data.current_ratio is not None:
            if data.current_ratio > 1.5:
                score_metric("liquidity", _WEIGHTS["liquidity"], 1.0, "bullish", "healthy_liquidity")
            elif data.current_ratio < 1.0:
                score_metric("liquidity", _WEIGHTS["liquidity"], 0.0, "bearish", "weak_liquidity")
            else:
                score_metric("liquidity", _WEIGHTS["liquidity"], 0.5, "neutral", "adequate_liquidity")

        if data.roe is not None:
            if data.roe > 0.20:
                score_metric("roe", _WEIGHTS["roe"], 1.0, "bullish", "high_roe")
            elif data.roe < 0.08:
                score_metric("roe", _WEIGHTS["roe"], 0.0, "bearish", "low_roe")
            else:
                score_metric("roe", _WEIGHTS["roe"], 0.5, "neutral", "moderate_roe")

        coverage = weighted_total / sum(_WEIGHTS.values())
        score = 50.0 if weighted_total == 0 else round(100 * weighted_sum / weighted_total, 2)

        required_fields = [
            "eps", "book_value_per_share", "revenue_ttm", "revenue_ttm_prev_year",
            "net_income_ttm", "net_income_ttm_prev_year", "operating_margin",
            "net_margin", "debt_to_equity", "current_ratio", "roe",
        ]
        missing_inputs = [f for f in required_fields if getattr(data, f) is None]

        return FundamentalResult(
            symbol=data.symbol,
            as_of=data.as_of,
            metrics=metrics,
            signals=signals,
            score=max(0.0, min(100.0, score)),
            factors=factors,
            missing_inputs=missing_inputs,
            coverage=round(coverage, 3),
        )
