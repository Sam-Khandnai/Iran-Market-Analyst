from datetime import date
from typing import Any

from pydantic import ValidationError

from market_analyst.data.errors import SymbolNotFound, TSETMCError
from market_analyst.data.models import ClientTypeSnapshot, DailyPrice, Instrument
from market_analyst.schemas.request import normalize_persian


def symbol_key(s: str) -> str:
    """کلید مقایسه: یکسان‌سازی ی/ک، حذف فاصله و نیم‌فاصله."""
    return normalize_persian(s).replace("\u200c", "").replace(" ", "")


def _to_date(v: Any) -> date:
    s = str(int(v))
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def _num(v: Any, default: float | None = None) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _int(v: Any) -> int | None:
    n = _num(v)
    return int(n) if n is not None else None


def parse_search_hits(payload: dict) -> list[dict]:
    if "instrumentSearch" not in payload:
        raise TSETMCError(f"ساختار جستجو غیرمنتظره: keys={list(payload)}")
    return payload["instrumentSearch"] or []


def pick_hit(hits: list[dict], symbol: str) -> dict:
    key = symbol_key(symbol)
    matches = [h for h in hits if symbol_key(h.get("lVal18AFC", "")) == key]
    if not matches:
        suggestions = [normalize_persian(h.get("lVal18AFC", "")) for h in hits[:5]]
        raise SymbolNotFound(symbol, suggestions)
    # اگر چند نتیجه دقیق بود، آنکه آخرین تاریخ معامله دارد
    return max(matches, key=lambda h: h.get("lastDate") or 0)


def parse_instrument(hit: dict, info_payload: dict) -> Instrument:
    if "instrumentInfo" not in info_payload:
        raise TSETMCError(f"ساختار اطلاعات نماد غیرمنتظره: keys={list(info_payload)}")
    info = info_payload["instrumentInfo"] or {}
    eps = info.get("eps") or {}
    sector = info.get("sector") or {}
    return Instrument(
        ins_code=str(hit["insCode"]),
        symbol=normalize_persian(hit.get("lVal18AFC", "")),
        name=normalize_persian(hit.get("lVal30") or info.get("lVal30", "")),
        isin=info.get("cIsin"),
        sector_code=str(sector.get("cSecVal") or info.get("cSecVal") or "") or None,
        sector_name=normalize_persian(sector["lSecVal"]) if sector.get("lSecVal") else None,
        shares_outstanding=_int(info.get("zTitad")),
        base_volume=_int(info.get("baseVol")),
        eps=_num(eps.get("estimatedEPS")),
        sector_pe=_num(eps.get("sectorPE")),
        market_flow=_int(info.get("flow") or hit.get("flow")),
    )


def parse_daily_prices(payload: dict, ins_code: str) -> tuple[list[DailyPrice], int]:
    """خروجی: (کندل‌های معتبر صعودی بدون تکرار، تعداد ردیف‌های ردشده)."""
    if "closingPriceDaily" not in payload:
        raise TSETMCError(f"ساختار تاریخچه غیرمنتظره: keys={list(payload)}")

    by_date: dict[date, DailyPrice] = {}
    dropped = 0
    for row in payload["closingPriceDaily"] or []:
        try:
            p = DailyPrice(
                ins_code=ins_code,
                trade_date=_to_date(row["dEven"]),
                open=row["priceFirst"],
                high=row["priceMax"],
                low=row["priceMin"],
                close=row["pClosing"],
                last=row["pDrCotVal"],
                yesterday=row["priceYesterday"],
                volume=int(row["qTotTran5J"]),
                value=int(row["qTotCap"]),
                trades=int(row["zTotTran"]),
            )
            by_date[p.trade_date] = p
        except (KeyError, ValueError, TypeError, ValidationError):
            dropped += 1
    return [by_date[d] for d in sorted(by_date)], dropped


def parse_client_type_history(payload: dict, ins_code: str) -> tuple[list[ClientTypeSnapshot], int]:
    if "clientType" not in payload:
        raise TSETMCError(f"ساختار حقیقی/حقوقی غیرمنتظره: keys={list(payload)}")

    rows: list[ClientTypeSnapshot] = []
    dropped = 0
    for row in payload["clientType"] or []:
        try:
            rows.append(ClientTypeSnapshot(
                ins_code=ins_code,
                trade_date=_to_date(row["recDate"]),
                buy_individual_volume=int(row["buy_I_Volume"]),
                buy_legal_volume=int(row["buy_N_Volume"]),
                buy_individual_count=int(row["buy_I_Count"]),
                buy_legal_count=int(row["buy_N_Count"]),
                sell_individual_volume=int(row["sell_I_Volume"]),
                sell_legal_volume=int(row["sell_N_Volume"]),
                sell_individual_count=int(row["sell_I_Count"]),
                sell_legal_count=int(row["sell_N_Count"]),
            ))
        except (KeyError, ValueError, TypeError, ValidationError):
            dropped += 1
    rows.sort(key=lambda r: r.trade_date)
    return rows, dropped