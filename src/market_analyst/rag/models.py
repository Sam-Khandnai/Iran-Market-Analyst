from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

DocType = Literal["financial_report", "company_report", "news", "regulation", "official"]


class DocumentInput(BaseModel):
    document_id: str
    doc_type: DocType
    source: str
    symbol: str | None = None
    title: str | None = None
    published_at: date | None = None
    text: str = Field(..., min_length=1)


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    doc_type: DocType
    source: str
    symbol: str | None = None
    title: str | None = None
    published_at: date | None = None
    text: str


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float = Field(..., ge=-1.0, le=1.0)