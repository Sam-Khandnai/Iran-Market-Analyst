import pytest
from pydantic import ValidationError

from market_analyst.schemas.report import AnalysisReport, Decision, Signal
from market_analyst.schemas.request import AnalysisRequest


def test_symbol_normalization():
    req = AnalysisRequest(symbol="  فولاد  ")
    assert req.symbol == "فولاد"
    assert AnalysisRequest(symbol="كيان").symbol == "کیان"  # ک/ی عربی -> فارسی


def test_defaults():
    req = AnalysisRequest(symbol="فولاد")
    assert req.timeframe.value == "daily"
    assert req.analysis_period.value == "1y"


def test_empty_symbol_rejected():
    with pytest.raises(ValidationError):
        AnalysisRequest(symbol="   ")


def test_confidence_bounds():
    with pytest.raises(ValidationError):
        Decision(signal=Signal.WATCH, confidence=1.5)


def test_report_shape():
    r = AnalysisReport(symbol="فولاد")
    data = r.model_dump()
    for key in [
        "technical_analysis", "fundamental_analysis", "market_context",
        "news_analysis", "risk_analysis", "decision",
        "key_factors", "risks", "evidence", "summary",
    ]:
        assert key in data