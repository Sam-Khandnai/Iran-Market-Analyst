from datetime import UTC, datetime

from pydantic import ValidationError

from market_analyst.data.assets.models import ASSET_CATALOG, AssetQuote


def _num(v) -> float | None:
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def parse_quotes(payload: dict) -> tuple[list[AssetQuote], int]:
    quotes: list[AssetQuote] = []
    dropped = 0
    now = datetime.now(UTC)

    for key, (title, category, unit) in ASSET_CATALOG.items():
        raw = payload.get(key)
        if raw is None:
            dropped += 1
            continue
        # فرمت رایج نوسان: {"value": "580000", "change": "500"} یا مقدار مستقیم عددی
        value = _num(raw.get("value") if isinstance(raw, dict) else raw)
        change = _num(raw.get("change")) if isinstance(raw, dict) else 0.0
        if value is None:
            dropped += 1
            continue
        try:
            quotes.append(AssetQuote(
                key=key, title=title, category=category, unit=unit,
                value=value, change=change or 0.0, fetched_at=now,
            ))
        except ValidationError:
            dropped += 1
    return quotes, dropped