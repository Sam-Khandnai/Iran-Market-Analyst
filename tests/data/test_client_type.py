import httpx
import pytest

from market_analyst.config import Settings
from market_analyst.data.errors import TSETMCError
from market_analyst.data.market_context_service import (
    get_latest_real_money_ratio,
    real_money_net_ratio,
)
from market_analyst.data.models import ClientTypeSnapshot
from market_analyst.data.tsetmc.client import TSETMCClient
from market_analyst.data.tsetmc.parsers import parse_client_type_history

PAYLOAD = {
    "clientType": [
        {
            "recDate": 20240101, "buy_I_Volume": 100, "buy_N_Volume": 50,
            "buy_I_Count": 10, "buy_N_Count": 2,
            "sell_I_Volume": 40, "sell_N_Volume": 110,
            "sell_I_Count": 8, "sell_N_Count": 1,
        },
        {"recDate": 20240102, "buy_I_Volume": "x"},  # ردیف خراب
    ]
}


def test_parse_drops_invalid_rows_and_sorts():
    rows, dropped = parse_client_type_history(PAYLOAD, "222")
    assert len(rows) == 1
    assert dropped == 1
    assert rows[0].trade_date.day == 1


def test_real_money_net_ratio_positive_means_individual_net_buying():
    snap = ClientTypeSnapshot(
        ins_code="222", trade_date=__import__("datetime").date(2024, 1, 1),
        buy_individual_volume=100, buy_legal_volume=50,
        buy_individual_count=10, buy_legal_count=2,
        sell_individual_volume=40, sell_legal_volume=110,
        sell_individual_count=8, sell_legal_count=1,
    )
    ratio = real_money_net_ratio(snap)
    assert ratio == round((100 - 40) / 150, 4)


def test_zero_total_volume_returns_none():
    snap = ClientTypeSnapshot(
        ins_code="222", trade_date=__import__("datetime").date(2024, 1, 1),
        buy_individual_volume=0, buy_legal_volume=0,
        buy_individual_count=0, buy_legal_count=0,
        sell_individual_volume=0, sell_legal_volume=0,
        sell_individual_count=0, sell_legal_count=0,
    )
    assert real_money_net_ratio(snap) is None


async def test_service_end_to_end_with_mock_transport():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=PAYLOAD)

    client = TSETMCClient(Settings(), transport=httpx.MockTransport(handler))
    ratio = await get_latest_real_money_ratio("222", client=client)
    assert ratio == round((100 - 40) / 150, 4)
    await client.aclose()


async def test_service_raises_on_empty_history():
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"clientType": []})

    client = TSETMCClient(Settings(), transport=httpx.MockTransport(handler))
    with pytest.raises(TSETMCError):
        await get_latest_real_money_ratio("222", client=client)
    await client.aclose()