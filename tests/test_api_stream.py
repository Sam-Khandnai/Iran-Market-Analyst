import pytest
from fastapi.testclient import TestClient

from market_analyst.api.routes import get_graph
from market_analyst.main import app
from market_analyst.schemas.report import AnalysisReport

client = TestClient(app)


class FakeStreamGraph:
    async def astream(self, state, stream_mode="updates"):
        yield {"data": {}}
        yield {"technical": {}}
        yield {"explanation": {"report": AnalysisReport(symbol=state["symbol"], summary="خلاصه فیک")}}


@pytest.fixture(autouse=True)
def _override_graph():
    app.dependency_overrides[get_graph] = lambda: FakeStreamGraph()
    yield
    app.dependency_overrides.pop(get_graph, None)


def test_stream_endpoint_returns_sse_events():
    with client.stream("POST", "/v1/analyze/stream", json={"symbol": "فولاد"}) as r:
        body = "".join(r.iter_text())
    assert '"event": "node"' in body
    assert '"event": "done"' in body
    assert "خلاصه فیک" in body