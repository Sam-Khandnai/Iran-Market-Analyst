from market_analyst.data.assets.parser import parse_quotes

PAYLOAD = {
    "usd": {"value": "580000", "change": "500"},
    "bub_18ayar": {"value": "35000000", "change": "-10000"},
    "bub_sekkeh": {"value": "420000000"},
}


def test_parses_known_keys():
    quotes, _dropped = parse_quotes(PAYLOAD)
    keys = {q.key for q in quotes}
    assert {"usd", "bub_18ayar", "bub_sekkeh"}.issubset(keys)
    usd = next(q for q in quotes if q.key == "usd")
    assert usd.value == 580000 and usd.change == 500


def test_missing_keys_are_dropped_not_crashed():
    quotes, dropped = parse_quotes({"usd": {"value": "580000"}})
    assert dropped > 0
    assert len(quotes) == 1