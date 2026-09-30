import re
from datetime import date

from market_analyst.data.errors import TSETMCError

_TAG_RE = re.compile(r"<[^>]+>")


def _clean_number(s: str) -> float | None:
    text = _TAG_RE.sub("", s).replace(",", "").replace("%", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def parse_history(payload: dict) -> tuple[list[dict], int]:
    """هر ردیف: [open, low, high, close, change_abs, change_pct, date_gregorian, date_jalali]."""
    rows = payload.get("data")
    if rows is None:
        raise TSETMCError(f"ساختار tgju غیرمنتظره: keys={list(payload)}")

    out: list[dict] = []
    dropped = 0
    for row in rows:
        try:
            close = _clean_number(row[3])
            greg = row[6]
            y, m, d = (int(x) for x in greg.split("/"))
            if close is None:
                dropped += 1
                continue
            out.append({
                "trade_date": date(y, m, d),
                "open": _clean_number(row[0]),
                "low": _clean_number(row[1]),
                "high": _clean_number(row[2]),
                "close": close,
            })
        except (IndexError, ValueError, TypeError):
            dropped += 1
    out.sort(key=lambda r: r["trade_date"])
    return out, dropped
