from market_analyst.data.errors import TSETMCError
from market_analyst.data.models import ClientTypeSnapshot
from market_analyst.data.tsetmc.client import TSETMCClient
from market_analyst.data.tsetmc.parsers import parse_client_type_history


def real_money_net_ratio(snapshot: ClientTypeSnapshot) -> float | None:
    """نسبت خالص حجم خرید حقیقی به کل حجم؛ در [-1, 1]."""
    total = snapshot.buy_individual_volume + snapshot.buy_legal_volume
    if total == 0:
        return None
    net = snapshot.buy_individual_volume - snapshot.sell_individual_volume
    return round(net / total, 4)


async def get_latest_real_money_ratio(
    ins_code: str, client: TSETMCClient | None = None
) -> float | None:
    owns_client = client is None
    client = client or TSETMCClient()
    try:
        rows, _ = parse_client_type_history(
            await client.client_type_history(ins_code), ins_code
        )
        if not rows:
            raise TSETMCError(f"تاریخچه حقیقی/حقوقی برای {ins_code} خالی است")
        return real_money_net_ratio(rows[-1])
    finally:
        if owns_client:
            await client.aclose()