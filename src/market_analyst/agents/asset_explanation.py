import json

from market_analyst.engines.asset_trend.signal_engine import AssetSignalResult
from market_analyst.llm.openrouter import ChatClient

_SYSTEM = (
    "شما یک دستیار توضیح‌دهنده بازار طلا و ارز هستید. بر اساس داده‌های JSON زیر که "
    "قبلاً توسط موتورهای قطعی محاسبه شده‌اند، یک خلاصه تحلیلی ۲ تا ۴ جمله‌ای فارسی بنویسید. "
    "هیچ عدد جدیدی اختراع نکنید و توصیه خرید/فروش شخصی ندهید."
)


class AssetExplanationAgent:
    def __init__(self, llm: ChatClient | None):
        self._llm = llm

    async def explain(self, title: str, result: AssetSignalResult) -> str:
        if self._llm is None:
            return self._fallback(title, result)
        try:
            facts = {"title": title, **result.to_dict()}
            prompt = f"{_SYSTEM}\n\nداده‌ها:\n{json.dumps(facts, ensure_ascii=False, indent=2)}"
            return await self._llm.ainvoke(prompt)
        except Exception:  # noqa: BLE001 — مرز مقاومت عمدی
            return self._fallback(title, result)

    def _fallback(self, title: str, result: AssetSignalResult) -> str:
        return (
            f"روند {title}: سیگنال {result.signal.value} با سطح اطمینان {result.confidence:.0%}. "
            "این خروجی صرفاً یک تحلیل پژوهشی مبتنی بر داده است."
        )