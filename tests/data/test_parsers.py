import pytest

from market_analyst.data.errors import SymbolNotFound, TSETMCError
from market_analyst.data.tsetmc.parsers import (
    parse_daily_prices,
    parse_instrument,
    parse_search_hits,
    pick_hit,
)

SEARCH = {
    "instrumentSearch": [
        {"insCode": "111", "lVal18AFC": "فولادح", "lVal30": "فولاد-ح", "lastDate": 20240101},
        {"insCode": "222", "lVal18AFC": "فولاد", "lVal30": "فولاد مبارکه اصفهان", "flow": 1, "lastDate": 20240301},
    ]
}
INFO = {
    "instrumentInfo": {
        "cIsin": "IRO1FOLZ0001",
        "zTitad": 25000000000,
        "baseVol": 1500000,
        "eps": {"estimatedEPS": "550", "sectorPE": "7.5"},
        "sector": {"cSecVal": "27", "lSecVal": "فلزات اساسی"},
    }
}


def _row(d, close=1000, high=1100, low=900, vol=1000):
    return {
        "dEven": d, "priceFirst": 950, "priceMax": high, "priceMin": low,
        "pClosing": close, "pDrCotVal": close, "priceYesterday": 940,
        "qTotTran5J": vol, "qTotCap": vol * close, "zTotTran": 10,
    }


def test_pick_exact_symbol_with_arabic_letters():
    hit = pick_hit(parse_search_hits(SEARCH), "فولاد")
    assert hit["insCode"] == "222"
    hits = {"instrumentSearch": [{"insCode": "9", "lVal18AFC": "كيان"}]}
    assert pick_hit(parse_search_hits(hits), "کیان")["insCode"] == "9"


def test_symbol_not_found_has_suggestions():
    with pytest.raises(SymbolNotFound) as e:
        pick_hit(parse_search_hits(SEARCH), "ناموجود")
    assert "فولاد" in e.value.suggestions


def test_parse_instrument():
    hit = pick_hit(parse_search_hits(SEARCH), "فولاد")
    inst = parse_instrument(hit, INFO)
    assert inst.ins_code == "222"
    assert inst.sector_name == "فلزات اساسی"
    assert inst.eps == 550.0 and inst.sector_pe == 7.5
    assert inst.shares_outstanding == 25_000_000_000


def test_prices_sorted_deduped_and_invalid_dropped():
    payload = {
        "closingPriceDaily": [
            _row(20240103), _row(20240101), _row(20240101),   # تکراری
            _row(20240102, high=800, low=900),                # high<low
            {"dEven": 20240104},                              # ناقص
        ]
    }
    prices, dropped = parse_daily_prices(payload, "222")
    assert [p.trade_date.day for p in prices] == [1, 3]
    assert dropped == 2


def test_unexpected_structure_raises():
    with pytest.raises(TSETMCError):
            parse_daily_prices({"foo": []}, "222")