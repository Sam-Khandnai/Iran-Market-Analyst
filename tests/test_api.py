import pytest
from fastapi.testclient import TestClient

from market_analyst.api.routes import get_graph
from market_analyst.main import app
from market_analyst.schemas.report import AnalysisReport

client = TestClient(app)


class FakeGraph:
    async def ainvoke(self, state: dict) -> dict:
        return {"report": AnalysisReport(symbol=state["symbol"], summary="خلاصه فیک")}


@pytest.fixture(autouse=True)
def _override_graph():
    app.dependency_overrides[get_graph] = lambda: FakeGraph()
    yield
    app.dependency_overrides.pop(get_graph, None)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_analyze_validation():
    r = client.post("/v1/analyze", json={"symbol": ""})
    assert r.status_code == 422


def test_analyze_returns_report_via_fake_graph():
    r = client.post("/v1/analyze", json={"symbol": "فولاد"})
    assert r.status_code == 200
    assert r.json()["summary"] == "خلاصه فیک"