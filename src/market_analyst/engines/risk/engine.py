import statistics

from market_analyst.engines.risk.models import RiskInput, RiskResult, RiskSignal

_WEIGHTS = {
    "volatility": 20,
    "liquidity": 20,
    "leverage": 15,
    "market_regime": 15,
    "concentration": 10,
    "trend_drawdown": 10,
    "data_quality": 10,
}

_LIQUID_THRESHOLD = 50_000_000_000     # ۵۰ میلیارد ریال
_ILLIQUID_THRESHOLD = 5_000_000_000    # ۵ میلیارد ریال


def _r(x: float | None, nd: int = 4) -> float | None:
    return None if x is None else round(x, nd)


class RiskEngine:
    def analyze(self, data: RiskInput) -> RiskResult:
        risk_factors: dict[str, RiskSignal] = {}
        contributing_factors: list[str] = []
        weighted_sum = 0.0
        weighted_total = 0.0

        def add(key: str, weight: int, sub: float | None, sig: RiskSignal, factor: str) -> None:
            nonlocal weighted_sum, weighted_total
            if sub is None:
                return
            weighted_sum += weight * sub
            weighted_total += weight
            risk_factors[key] = sig
            contributing_factors.append(factor)

        # --- نوسان‌پذیری (از Technical: ATR نسبت به قیمت) ---
        atr_pct = None
        if data.technical is not None:
            atr14 = data.technical.indicators.get("atr_14")
            price = data.technical.price
            if atr14 is not None and price:
                atr_pct = atr14 / price
        if atr_pct is not None:
            if atr_pct > 0.05:
                add("volatility", _WEIGHTS["volatility"], 1.0, "high", "high_volatility")
            elif atr_pct < 0.02:
                add("volatility", _WEIGHTS["volatility"], 0.0, "low", "low_volatility")
            else:
                add("volatility", _WEIGHTS["volatility"], 0.5, "medium", "moderate_volatility")

        # --- نقدشوندگی مطلق ---
        if data.avg_daily_value_rial is not None:
            v = data.avg_daily_value_rial
            if v >= _LIQUID_THRESHOLD:
                add("liquidity", _WEIGHTS["liquidity"], 0.0, "low", "liquid_market")
            elif v < _ILLIQUID_THRESHOLD:
                add("liquidity", _WEIGHTS["liquidity"], 1.0, "high", "illiquid_market")
            else:
                add("liquidity", _WEIGHTS["liquidity"], 0.5, "medium", "moderate_liquidity")

        # --- اهرم مالی (از Fundamental) ---
        de = data.fundamental.metrics.get("debt_to_equity") if data.fundamental else None
        if de is not None:
            if de < 0.5:
                add("leverage", _WEIGHTS["leverage"], 0.0, "low", "low_leverage_risk")
            elif de > 1.5:
                add("leverage", _WEIGHTS["leverage"], 1.0, "high", "high_leverage_risk")
            else:
                add("leverage", _WEIGHTS["leverage"], 0.5, "medium", "moderate_leverage_risk")

        # --- رژیم بازار (از Market Context) ---
        if data.market_context is not None:
            regime = data.market_context.market_regime
            if regime == "risk_off":
                add("market_regime", _WEIGHTS["market_regime"], 1.0, "high", "market_regime_risk_off")
            elif regime == "risk_on":
                add("market_regime", _WEIGHTS["market_regime"], 0.0, "low", "market_regime_risk_on")
            else:
                add("market_regime", _WEIGHTS["market_regime"], 0.5, "medium", "market_regime_neutral")

        # --- تمرکز مالکیت (سهام شناور آزاد) ---
        if data.free_float_ratio is not None:
            ff = data.free_float_ratio
            if ff < 0.15:
                add("concentration", _WEIGHTS["concentration"], 1.0, "high", "low_free_float")
            elif ff > 0.40:
                add("concentration", _WEIGHTS["concentration"], 0.0, "low", "high_free_float")
            else:
                add("concentration", _WEIGHTS["concentration"], 0.5, "medium", "moderate_free_float")

        # --- روند نزولی به‌عنوان ریسک افت بیشتر ---
        if data.technical is not None:
            trend = data.technical.trend
            if trend == "downtrend":
                add("trend_drawdown", _WEIGHTS["trend_drawdown"], 1.0, "high", "downtrend_risk")
            elif trend == "uptrend":
                add("trend_drawdown", _WEIGHTS["trend_drawdown"], 0.0, "low", "uptrend_supportive")
            else:
                add("trend_drawdown", _WEIGHTS["trend_drawdown"], 0.5, "medium", "sideways_uncertain")

        # --- کیفیت داده (کم بودن پوشش/تاریخچه یعنی نااطمینانی بیشتر) ---
        quality_points: list[float] = []
        if data.technical is not None:
            n = data.technical.data_points
            quality_points.append(1.0 if n >= 200 else (0.5 if n >= 60 else 0.0))
        if data.fundamental is not None:
            quality_points.append(data.fundamental.coverage)
        if data.market_context is not None:
            quality_points.append(data.market_context.coverage)
        if quality_points:
            avg_quality = statistics.mean(quality_points)
            sub = 1.0 - avg_quality
            if sub > 0.6:
                add("data_quality", _WEIGHTS["data_quality"], sub, "high", "low_data_quality")
            elif sub < 0.2:
                add("data_quality", _WEIGHTS["data_quality"], sub, "low", "high_data_quality")
            else:
                add("data_quality", _WEIGHTS["data_quality"], sub, "medium", "moderate_data_quality")

        coverage = weighted_total / sum(_WEIGHTS.values())
        risk_score = 50.0 if weighted_total == 0 else round(100 * weighted_sum / weighted_total, 2)
        risk_score = max(0.0, min(100.0, risk_score))

        if risk_score >= 65:
            level = "high"
        elif risk_score <= 35:
            level = "low"
        else:
            level = "medium"

        missing_inputs: list[str] = []
        if data.technical is None:
            missing_inputs.append("technical")
        if data.fundamental is None:
            missing_inputs.append("fundamental")
        if data.market_context is None:
            missing_inputs.append("market_context")
        if data.avg_daily_value_rial is None:
            missing_inputs.append("avg_daily_value_rial")
        if data.free_float_ratio is None:
            missing_inputs.append("free_float_ratio")

        metrics = {
            "atr_pct": _r(atr_pct),
            "avg_daily_value_rial": _r(data.avg_daily_value_rial, 0),
            "debt_to_equity": _r(de),
            "market_regime": data.market_context.market_regime if data.market_context else None,
            "free_float_ratio": _r(data.free_float_ratio),
            "trend": data.technical.trend if data.technical else None,
        }

        return RiskResult(
            symbol=data.symbol,
            as_of=data.as_of,
            metrics=metrics,
            risk_factors=risk_factors,
            risk_score=risk_score,
            risk_level=level,
            contributing_factors=contributing_factors,
            missing_inputs=missing_inputs,
            coverage=round(coverage, 3),
        )