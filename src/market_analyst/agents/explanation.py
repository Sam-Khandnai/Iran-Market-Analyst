import json

from market_analyst.engines.decision.models import DecisionResult
from market_analyst.engines.risk.models import RiskResult
from market_analyst.llm.openrouter import ChatClient

_SYSTEM_INSTRUCTION = (
    "شما یک دستیار توضیح‌دهنده مالی هستید. بر اساس داده‌های JSON زیر که قبلاً "
    "توسط موتورهای قطعی (نه شما) محاسبه شده‌اند، یک خلاصه تحلیلی ۳ تا ۵ جمله‌ای "
    "به زبان فارسی بنویسید. هیچ عدد یا واقعیت جدیدی اختراع نکنید، سیگنال خرید/فروش "
    "تولید نکنید و توصیه شخصی سرمایه‌گذاری ندهید؛ فقط داده‌های داده‌شده و اسناد مرجع "
    "(در صورت وجود) را تفسیر کنید."
)


class ExplanationAgent:
    def __init__(self, llm: ChatClient | None):
        self._llm = llm

    async def explain(
        self,
        decision: DecisionResult | None,
        risk: RiskResult | None,
        retrieved_context: list[str] | None = None,
    ) -> str:

        if decision is None:
            return "داده کافی برای تحلیل این نماد در دسترس نبود."

        if self._llm is None:
            return self._fallback(decision, risk)

        try:
            return await self._llm.ainvoke(
                self._build_prompt(
                    decision,
                    risk,
                    retrieved_context,
                )
            )
        except Exception:  # noqa: BLE001
            return self._fallback(decision, risk)
        
    def _fallback(self, decision: DecisionResult, risk: RiskResult | None) -> str:
        return (
            f"سیگنال سیستم برای {decision.symbol}: {decision.signal.value} "
            f"با سطح اطمینان {decision.confidence:.0%}. "
            f"سطح ریسک: {risk.risk_level if risk else 'نامشخص'}. "
            "این خروجی صرفاً یک تحلیل پژوهشی مبتنی بر داده است."
        )

    def _build_prompt(
        self, decision: DecisionResult, risk: RiskResult | None, retrieved_context: list[str] | None,
    ) -> str:
        facts = {
            "symbol": decision.symbol,
            "signal": decision.signal.value,
            "confidence": decision.confidence,
            "composite_score": decision.composite_score,
            "component_scores": decision.component_scores,
            "key_factors": decision.key_factors,
            "risks": decision.risks,
            "conflicts": decision.conflicts,
            "risk_level": risk.risk_level if risk else None,
        }
        prompt = f"{_SYSTEM_INSTRUCTION}\n\nداده‌ها:\n{json.dumps(facts, ensure_ascii=False, indent=2)}"
        if retrieved_context:
            joined = "\n---\n".join(retrieved_context[:5])
            prompt += f"\n\nاسناد مرجع مرتبط (فقط برای زمینه، عدد جدید از اینجا استخراج نکنید):\n{joined}"
        return prompt