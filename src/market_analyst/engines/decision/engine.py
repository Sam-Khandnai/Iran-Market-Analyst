from market_analyst.engines.decision.models import DecisionInput, DecisionResult
from market_analyst.schemas.report import Signal

_WEIGHTS = {"technical": 35, "fundamental": 30, "market_context": 20, "risk": 15}

_LEVELS = [
    Signal.STRONG_NEGATIVE, Signal.NEGATIVE, Signal.NEUTRAL,
    Signal.WATCH, Signal.POSITIVE, Signal.STRONG_POSITIVE,
]


def _direction(score: float) -> str:
    if score >= 55:
        return "bullish"
    if score <= 45:
        return "bearish"
    return "neutral"


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


def _downgrade(signal: Signal, steps: int = 1) -> Signal:
    idx = max(0, _LEVELS.index(signal) - steps)
    return _LEVELS[idx]


class DecisionEngine:
    def analyze(self, data: DecisionInput) -> DecisionResult:
        weighted_sum = 0.0
        weighted_total = 0.0
        component_scores: dict[str, float | None] = {
            "technical": None, "fundamental": None, "market_context": None, "risk_adjusted": None,
        }
        reliabilities: list[float] = []
        directions: dict[str, str] = {}
        key_factors: list[str] = []
        risks: list[str] = []

        if data.technical is not None:
            s = data.technical.score
            component_scores["technical"] = s
            weighted_sum += _WEIGHTS["technical"] * s
            weighted_total += _WEIGHTS["technical"]
            directions["technical"] = _direction(s)
            reliabilities.append(min(1.0, data.technical.data_points / 200))
            key_factors.extend(f"technical:{f}" for f in data.technical.factors[:3])

        if data.fundamental is not None:
            s = data.fundamental.score
            component_scores["fundamental"] = s
            weighted_sum += _WEIGHTS["fundamental"] * s
            weighted_total += _WEIGHTS["fundamental"]
            directions["fundamental"] = _direction(s)
            reliabilities.append(data.fundamental.coverage)
            key_factors.extend(f"fundamental:{f}" for f in data.fundamental.factors[:3])

        if data.market_context is not None:
            s = data.market_context.score
            component_scores["market_context"] = s
            weighted_sum += _WEIGHTS["market_context"] * s
            weighted_total += _WEIGHTS["market_context"]
            directions["market_context"] = _direction(s)
            reliabilities.append(data.market_context.coverage)
            key_factors.extend(f"market:{f}" for f in data.market_context.factors[:3])

        if data.risk is not None:
            risk_adjusted = 100 - data.risk.risk_score
            component_scores["risk_adjusted"] = risk_adjusted
            weighted_sum += _WEIGHTS["risk"] * risk_adjusted
            weighted_total += _WEIGHTS["risk"]
            reliabilities.append(data.risk.coverage)
            risks.extend(data.risk.contributing_factors[:5])

        coverage = weighted_total / sum(_WEIGHTS.values())
        composite_score = 50.0 if weighted_total == 0 else round(weighted_sum / weighted_total, 2)
        composite_score = max(0.0, min(100.0, composite_score))

        # اعتبارسنجی متقابل: تضاد بین جهت‌های Technical/Fundamental/Market
        dir_values = list(directions.values())
        pairs = [(a, b) for i, a in enumerate(dir_values) for b in dir_values[i + 1:]]
        conflicts: list[str] = []
        agreeing = 0
        for (name_a, dir_a), (name_b, dir_b) in [
            (pa, pb)
            for i, pa in enumerate(directions.items())
            for pb in list(directions.items())[i + 1:]
        ]:
            if dir_a != "neutral" and dir_b != "neutral" and dir_a != dir_b:
                conflicts.append(f"{name_a}_{dir_a}_vs_{name_b}_{dir_b}")
            else:
                agreeing += 1
        agreement_ratio = 1.0 if not pairs else agreeing / len(pairs)

        signal = _signal_from_score(composite_score)

        risk_level = data.risk.risk_level if data.risk is not None else None
        if risk_level == "high":
            signal = _downgrade(signal, 1)

        reliability_avg = sum(reliabilities) / len(reliabilities) if reliabilities else 0.0
        confidence = reliability_avg * (0.6 + 0.4 * agreement_ratio)
        if risk_level == "high":
            confidence *= 0.85
        confidence = round(max(0.0, min(1.0, confidence)), 2)

        missing_inputs = [
            name for name, val in [
                ("technical", data.technical), ("fundamental", data.fundamental),
                ("market_context", data.market_context), ("risk", data.risk),
            ] if val is None
        ]

        return DecisionResult(
            symbol=data.symbol,
            as_of=data.as_of,
            signal=signal,
            confidence=confidence,
            composite_score=composite_score,
            component_scores=component_scores,
            agreement_ratio=round(agreement_ratio, 3),
            conflicts=conflicts,
            key_factors=key_factors,
            risks=risks,
            missing_inputs=missing_inputs,
            coverage=round(coverage, 3),
        )