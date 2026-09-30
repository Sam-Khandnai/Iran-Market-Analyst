from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from market_analyst.agents.asset_explanation import AssetExplanationAgent
from market_analyst.data.assets.models import ASSET_CATALOG
from market_analyst.data.assets.service import get_all_quotes, get_asset_history
from market_analyst.engines.asset_trend.engine import AssetTrendEngine
from market_analyst.engines.asset_trend.signal_engine import AssetSignalEngine
from market_analyst.llm.openrouter import build_default_llm
from market_analyst.logging import get_logger

log = get_logger("api.assets")
router = APIRouter(prefix="/v1/assets")


def get_asset_llm():
    return build_default_llm()


LLMDep = Annotated[object, Depends(get_asset_llm)]


@router.get("/popular")
async def popular_assets() -> list[dict]:
    try:
        quotes = await get_all_quotes()
    except Exception as e:
        log.error("popular_assets_failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=502, detail=str(e)) from e
    return [q.model_dump(mode="json") for q in quotes]


@router.get("/{key}/trend")
async def asset_trend(key: str) -> dict:
    history = await get_asset_history(key)
    if not history:
        raise HTTPException(status_code=404, detail="تاریخچه‌ای برای این دارایی ثبت نشده است")
    result = AssetTrendEngine().analyze(key, history)
    return {
        "trend": result.model_dump(mode="json"),
        "history": [h.model_dump(mode="json") for h in history],
    }


@router.get("/{key}/analyze")
async def asset_analyze(key: str, llm: LLMDep) -> dict:
    if key not in ASSET_CATALOG:
        raise HTTPException(status_code=404, detail="دارایی ناشناخته است")
    title, category, unit = ASSET_CATALOG[key]

    history = await get_asset_history(key)
    if not history:
        raise HTTPException(status_code=404, detail="تاریخچه‌ای برای این دارایی ثبت نشده است")

    trend = AssetTrendEngine().analyze(key, history)
    signal_result = AssetSignalEngine().analyze(trend, history)
    summary = await AssetExplanationAgent(llm).explain(title, signal_result)

    return {
        "key": key,
        "title": title,
        "category": category,
        "unit": unit,
        "trend": trend.model_dump(mode="json"),
        "signal": signal_result.to_dict(),
        "summary": summary,
        "history": [h.model_dump(mode="json") for h in history],
        "disclaimer": "این خروجی صرفاً یک تحلیل پژوهشی مبتنی بر داده است و توصیه سرمایه‌گذاری نیست.",
    }