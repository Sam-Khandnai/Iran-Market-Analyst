from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class NewsHeadline(BaseModel):
    title: str
    source: str
    published_at: date | None = None
    sentiment: Literal["positive", "negative", "neutral"] = "neutral"


class NewsResult(BaseModel):
    symbol: str
    as_of: date
    sentiment: Literal["positive", "negative", "neutral"]
    score: float = Field(..., ge=0, le=100)
    headlines: list[NewsHeadline] = Field(default_factory=list)
    coverage: float = Field(..., ge=0, le=1)