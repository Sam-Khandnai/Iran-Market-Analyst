import hashlib
import math
import re
from typing import Protocol

from market_analyst.schemas.request import normalize_persian

_TOKEN_RE = re.compile(r"[\w\u0600-\u06FF]+")


class Embedder(Protocol):
    dimension: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashingEmbedder:
    """Bag-of-words هش‌شده و L2-normalize شده. بدون وابستگی خارجی و کاملاً deterministic.

    برای جایگزینی با مدل embedding واقعی (مثلاً sentence-transformers)، همین رابط
    Embedder را با متد embed پیاده‌سازی کنید؛ بقیه سیستم بدون تغییر کار می‌کند.
    """

    def __init__(self, dimension: int = 256):
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vec = [0.0] * self.dimension
        tokens = _TOKEN_RE.findall(normalize_persian(text).lower())
        for tok in tokens:
            idx = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16) % self.dimension
            vec[idx] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec
        return [v / norm for v in vec]