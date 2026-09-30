from market_analyst.engines.market_context.models import (
    MarketContextInput,
    MarketContextResult,
    Signal,
)

_WEIGHTS = {
    "market_trend": 15,
    "market_breadth": 10,
    "sector_trend": 20,
    "sector_vs_market": 15,
    "symbol_vs_sector": 20,
    "money_flow": 15,
    "queue": 5,
}

_REQUIRED = [
    "market_index_change_1m", "market_breadth",
    "sector_index_change_1m", "sector_rank", "total_sectors",
    "symbol_return_1m", "real_money_net_ratio", "volume_relative_to_avg",
]


def _r(x: float | None, nd: int = 4) -> float | None:
    return None if x is None else round(x, nd)


class MarketContextEngine:
    def analyze(self, data: MarketContextInput) -> MarketContextResult:
        sector_vs_market = None
        if data.sector_index_change_1m is not None and data.market_index_change_1m is not None:
            sector_vs_market = data.sector_index_change_1m - data.market_index_change_1m

        symbol_vs_sector = None
        if data.symbol_return_1m is not None and data.sector_index_change_1m is not None:
            symbol_vs_sector = data.symbol_return_1m - data.sector_index_change_1m

        symbol_vs_market = None
        if data.symbol_return_1m is not None and data.market_index_change_1m is not None:
            symbol_vs_market = data.symbol_return_1m - data.market_index_change_1m

        sector_percentile = None
        if data.sector_rank is not None and data.total_sectors and data.total_sectors > 0:
            sector_percentile = 1 - (data.sector_rank - 1) / data.total_sectors  # 1=بهترین

        metrics = {
            "market_index_change_1m": _r(data.market_index_change_1m),
            "market_breadth": _r(data.market_breadth),
            "sector_index_change_1m": _r(data.sector_index_change_1m),
            "sector_vs_market": _r(sector_vs_market),
            "sector_percentile": _r(sector_percentile),
            "symbol_return_1m": _r(data.symbol_return_1m),
            "symbol_vs_sector": _r(symbol_vs_sector),
            "symbol_vs_market": _r(symbol_vs_market),
            "real_money_net_ratio": _r(data.real_money_net_ratio),
            "volume_relative_to_avg": _r(data.volume_relative_to_avg),
            "queue_state": data.queue_state,
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

        # روند کل بازار
        if data.market_index_change_1m is not None:
            if data.market_index_change_1m > 0.03:
                score_metric("market_trend", _WEIGHTS["market_trend"], 1.0, "bullish", "market_uptrend")
            elif data.market_index_change_1m < -0.03:
                score_metric("market_trend", _WEIGHTS["market_trend"], 0.0, "bearish", "market_downtrend")
            else:
                score_metric("market_trend", _WEIGHTS["market_trend"], 0.5, "neutral", "market_flat")

        # وسعت بازار (breadth)
        if data.market_breadth is not None:
            if data.market_breadth > 0.2:
                score_metric("market_breadth", _WEIGHTS["market_breadth"], 1.0, "bullish", "broad_market_strength")
            elif data.market_breadth < -0.2:
                score_metric("market_breadth", _WEIGHTS["market_breadth"], 0.0, "bearish", "broad_market_weakness")
            else:
                score_metric("market_breadth", _WEIGHTS["market_breadth"], 0.5, "neutral", "mixed_breadth")

        # روند صنعت
        if data.sector_index_change_1m is not None:
            if data.sector_index_change_1m > 0.03:
                score_metric("sector_trend", _WEIGHTS["sector_trend"], 1.0, "bullish", "sector_uptrend")
            elif data.sector_index_change_1m < -0.03:
                score_metric("sector_trend", _WEIGHTS["sector_trend"], 0.0, "bearish", "sector_downtrend")
            else:
                score_metric("sector_trend", _WEIGHTS["sector_trend"], 0.5, "neutral", "sector_flat")

        # صنعت نسبت به بازار
        if sector_vs_market is not None:
            if sector_vs_market > 0.02:
                score_metric("sector_vs_market", _WEIGHTS["sector_vs_market"], 1.0, "bullish", "sector_outperforming_market")
            elif sector_vs_market < -0.02:
                score_metric("sector_vs_market", _WEIGHTS["sector_vs_market"], 0.0, "bearish", "sector_underperforming_market")
            else:
                score_metric("sector_vs_market", _WEIGHTS["sector_vs_market"], 0.5, "neutral", "sector_in_line_with_market")

        # نماد نسبت به صنعت
        if symbol_vs_sector is not None:
            if symbol_vs_sector > 0.02:
                score_metric("symbol_vs_sector", _WEIGHTS["symbol_vs_sector"], 1.0, "bullish", "symbol_leading_sector")
            elif symbol_vs_sector < -0.02:
                score_metric("symbol_vs_sector", _WEIGHTS["symbol_vs_sector"], 0.0, "bearish", "symbol_lagging_sector")
            else:
                score_metric("symbol_vs_sector", _WEIGHTS["symbol_vs_sector"], 0.5, "neutral", "symbol_in_line_with_sector")

        # جریان پول حقیقی
        if data.real_money_net_ratio is not None:
            if data.real_money_net_ratio > 0.05:
                score_metric("money_flow", _WEIGHTS["money_flow"], 1.0, "bullish", "real_money_inflow")
            elif data.real_money_net_ratio < -0.05:
                score_metric("money_flow", _WEIGHTS["money_flow"], 0.0, "bearish", "real_money_outflow")
            else:
                score_metric("money_flow", _WEIGHTS["money_flow"], 0.5, "neutral", "balanced_money_flow")

        # صف خرید/فروش
        if data.queue_state is not None:
            if data.queue_state == "buy_queue":
                score_metric("queue", _WEIGHTS["queue"], 1.0, "bullish", "buy_queue_active")
            elif data.queue_state == "sell_queue":
                score_metric("queue", _WEIGHTS["queue"], 0.0, "bearish", "sell_queue_active")
            else:
                score_metric("queue", _WEIGHTS["queue"], 0.5, "neutral", "no_queue")

        coverage = weighted_total / sum(_WEIGHTS.values())
        score = 50.0 if weighted_total == 0 else round(100 * weighted_sum / weighted_total, 2)
        score = max(0.0, min(100.0, score))

        if score >= 65:
            regime = "risk_on"
        elif score <= 35:
            regime = "risk_off"
        else:
            regime = "neutral"

        missing_inputs = [f for f in _REQUIRED if getattr(data, f) is None]

        return MarketContextResult(
            symbol=data.symbol,
            as_of=data.as_of,
            metrics=metrics,
            signals=signals,
            score=score,
            market_regime=regime,
            factors=factors,
            missing_inputs=missing_inputs,
            coverage=round(coverage, 3),
        )