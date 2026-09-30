from datetime import date

import pytest

from market_analyst.data.assets.tgju_parser import parse_history
from market_analyst.data.errors import TSETMCError

PAYLOAD = {
    "data": [
        [
            "2,499,950", "2,493,600", "2,537,200", "2,537,000",
            '<span class="high" dir="ltr">89000</span>',
            '<span class="high" dir="ltr">3.64%</span>',
            "2026/09/29", "1405/07/07",
        ],
        [
            "2,405,000", "2,402,600", "2,450,200", "2,448,000",
            '<span class="high" dir="ltr">98000</span>',
            '<span class="high" dir="ltr">4.17%</span>',
            "2026/09/28", "1405/07/06",
        ],
        ["bad", "row"],  # ردیف خراب
    ]
}


def test_parses_valid_rows_and_drops_invalid():
    rows, dropped = parse_history(PAYLOAD)
    assert len(rows) == 2
    assert dropped == 1


def test_rows_sorted_ascending_by_date():
    rows, _ = parse_history(PAYLOAD)
    assert rows[0]["trade_date"] < rows[1]["trade_date"]
    assert rows[0]["trade_date"] == date(2026, 9, 28)


def test_close_value_cleaned_of_commas_and_html():
    rows, _ = parse_history(PAYLOAD)
    latest = rows[-1]
    assert latest["close"] == 2537000.0
    assert latest["open"] == 2499950.0


def test_missing_data_key_raises():
    with pytest.raises(TSETMCError):
        parse_history({"foo": []})