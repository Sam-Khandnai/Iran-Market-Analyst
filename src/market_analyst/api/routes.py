import json
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from market_analyst.config import get_settings
from market_analyst.graph.build import build_graph
from market_analyst.schemas.report import AnalysisReport
from market_analyst.schemas.request import AnalysisRequest

router = APIRouter()

_NODE_LABELS_FA = {
    "data": "دریافت داده از TSETMC",
    "technical": "تحلیل تکنیکال",
    "fundamental": "تحلیل بنیادی",
    "market_context": "تحلیل وضعیت بازار",
    "news": "بررسی اخبار",
    "risk": "ارزیابی ریسک",
    "decision": "تصمیم‌گیری",
    "explanation": "تولید توضیح نهایی",
}

@lru_cache
def _default_graph():
    return build_graph(use_mcp=get_settings().use_mcp)

def get_graph():
    return _default_graph()

GraphDep = Annotated[object, Depends(get_graph)]

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/v1/analyze", response_model=AnalysisReport)
async def analyze(req: AnalysisRequest, graph: GraphDep) -> AnalysisReport:
    result = await graph.ainvoke({
        "symbol": req.symbol,
        "timeframe": req.timeframe.value,
        "analysis_period": req.analysis_period.value,
        "errors": [],
    })
    report = result.get("report")
    if report is None:
        raise HTTPException(status_code=502, detail="pipeline failed to produce a report")
    return report



@router.post("/v1/analyze/stream")
async def analyze_stream(
    req: AnalysisRequest,
    graph: GraphDep,
):
    async def event_generator():
        state = {
            "symbol": req.symbol,
            "timeframe": req.timeframe.value,
            "analysis_period": req.analysis_period.value,
            "errors": [],
        }
        try:
            async for update in graph.astream(state, stream_mode="updates"):
                for node_name, node_output in update.items():
                    payload = {
                        "event": "node",
                        "node": node_name,
                        "label": _NODE_LABELS_FA.get(node_name, node_name),
                    }
                    if node_name == "explanation" and node_output.get("report") is not None:
                        payload["report"] = node_output["report"].model_dump(mode="json")
                    yield f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
            yield f"data: {json.dumps({'event': 'done'}, ensure_ascii=False)}\n\n"
        except Exception as e:  # noqa: BLE001 — استریم نباید بدون پیام خطا به کلاینت قطع شود
            yield f"data: {json.dumps({'event': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

