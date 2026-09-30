from datetime import date

from market_analyst.engines.news.models import NewsHeadline, NewsResult
from market_analyst.rag.models import RetrievedChunk
from market_analyst.schemas.request import normalize_persian

_POSITIVE_WORDS = {
    "رشد", "افزایش", "سود", "صعود", "مثبت", "رونق", "بهبود", "جهش", "قوی", "موفق",
}
_NEGATIVE_WORDS = {
    "کاهش", "زیان", "ضرر", "نزول", "منفی", "بحران", "تحریم", "افت", "ضعیف", "ریسک",
}


def _sentiment_of(text: str) -> float:
    """امتیاز احساسی در [-1, 1] بر اساس شمارش کلمات لغت‌نامه؛ کاملاً deterministic."""
    words = normalize_persian(text).split()
    pos = sum(1 for w in words if w in _POSITIVE_WORDS)
    neg = sum(1 for w in words if w in _NEGATIVE_WORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


class NewsEngine:
    def analyze(self, symbol: str, as_of: date, chunks: list[RetrievedChunk]) -> NewsResult:
        if not chunks:
            return NewsResult(
                symbol=symbol, as_of=as_of, sentiment="neutral",
                score=50.0, headlines=[], coverage=0.0,
            )

        headlines: list[NewsHeadline] = []
        weighted_sentiment = 0.0
        weight_total = 0.0
        for rc in chunks:
            s = _sentiment_of(rc.chunk.text)
            label = "positive" if s > 0.15 else ("negative" if s < -0.15 else "neutral")
            weight = max(rc.score, 0.0) + 0.01  # جلوگیری از وزن صفر
            weighted_sentiment += s * weight
            weight_total += weight
            headlines.append(NewsHeadline(
                title=rc.chunk.title or rc.chunk.text[:60],
                source=rc.chunk.source,
                published_at=rc.chunk.published_at,
                sentiment=label,
            ))

        avg_sentiment = weighted_sentiment / weight_total if weight_total else 0.0
        score = max(0.0, min(100.0, 50.0 + avg_sentiment * 50.0))
        overall = "positive" if avg_sentiment > 0.15 else ("negative" if avg_sentiment < -0.15 else "neutral")
        coverage = min(1.0, len(chunks) / 5)

        return NewsResult(
            symbol=symbol, as_of=as_of, sentiment=overall,
            score=round(score, 2), headlines=headlines, coverage=round(coverage, 3),
        )