from datetime import date, timedelta

from market_analyst.data.models import DailyPrice


def make_prices(closes: list[float], ins_code: str = "X", volume: int = 1000) -> list[DailyPrice]:
    start = date(2024, 1, 1)
    out: list[DailyPrice] = []
    prev = closes[0]
    for i, c in enumerate(closes):
        out.append(
            DailyPrice(
                ins_code=ins_code,
                trade_date=start + timedelta(days=i),
                open=prev, high=max(prev, c) * 1.001, low=min(prev, c) * 0.999,
                close=c, last=c, yesterday=prev,
                volume=volume, value=int(volume * c), trades=50,
            )
        )
        prev = c
    return out