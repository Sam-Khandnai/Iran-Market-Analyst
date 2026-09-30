from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel

AssetCategory = Literal["currency", "gold", "coin"]

ASSET_CATALOG: dict[str, tuple[str, AssetCategory, str]] = {
    "usd": ("دلار آمریکا", "currency", "ریال"),
    "eur": ("یورو", "currency", "ریال"),
    "aed": ("درهم امارات", "currency", "ریال"),
    "bub_18ayar": ("طلای ۱۸ عیار (گرم)", "gold", "ریال"),
    "usd_xau": ("انس جهانی طلا", "gold", "دلار"),
    "bub_sekkeh": ("سکه امامی", "coin", "ریال"),
    "bub_bahar": ("سکه بهار آزادی", "coin", "ریال"),
    "bub_nim": ("نیم سکه", "coin", "ریال"),
    "bub_rob": ("ربع سکه", "coin", "ریال"),
    "bub_gerami": ("سکه گرمی", "coin", "ریال"),
}

class AssetQuote(BaseModel):
    key: str
    title: str
    category: AssetCategory
    unit: str
    value: float
    change: float = 0.0
    fetched_at: datetime


class AssetHistoryPoint(BaseModel):
    trade_date: date
    value: float