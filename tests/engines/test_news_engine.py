from datetime import date

from market_analyst.engines.news.engine import NewsEngine
from market_analyst.rag.models import Chunk, RetrievedChunk

engine = NewsEngine()
D = date(2024, 1, 1)


def _rc(text: str, score: float = 0.8, title: str | None = None) -> RetrievedChunk:
    chunk = Chunk(
        chunk_id="c1", document_id="d1", chunk_index=0, doc_type="news",
        source="خبرگزاری تست", symbol="فولاد", title=title, published_at=D, text=text,
    )
    return RetrievedChunk(chunk=chunk, score=score)


def test_no_chunks_gives_neutral_zero_coverage():
    result = engine.analyze("فولاد", D, [])
    assert result.sentiment == "neutral"
    assert result.score == 50.0
    assert result.coverage == 0.0


def test_positive_words_push_score_above_fifty():
    chunks = [_rc("رشد چشمگیر سود و افزایش تولید در فولاد مبارکه")]
    result = engine.analyze("فولاد", D, chunks)
    assert result.sentiment == "positive"
    assert result.score > 50.0
    assert result.headlines[0].sentiment == "positive"


def test_negative_words_push_score_below_fifty():
    chunks = [_rc("زیان سنگین و کاهش شدید سود به دلیل بحران و تحریم")]
    result = engine.analyze("فولاد", D, chunks)
    assert result.sentiment == "negative"
    assert result.score < 50.0


def test_neutral_text_without_lexicon_words_stays_neutral():
    chunks = [_rc("گزارش عملکرد فولاد مبارکه در سه‌ماهه سوم منتشر شد")]
    result = engine.analyze("فولاد", D, chunks)
    assert result.sentiment == "neutral"
    assert result.score == 50.0


def test_coverage_scales_with_number_of_chunks():
    few = engine.analyze("فولاد", D, [_rc("رشد سود")])
    many = engine.analyze("فولاد", D, [_rc("رشد سود")] * 5)
    assert many.coverage > few.coverage
    assert many.coverage == 1.0


def test_headline_title_falls_back_to_text_prefix_when_missing():
    chunks = [_rc("این یک متن خبری بدون عنوان مشخص است که باید بریده شود")]
    result = engine.analyze("فولاد", D, chunks)
    assert result.headlines[0].title.startswith("این یک متن خبری")


def test_score_always_within_bounds():
    chunks = [_rc("رشد رشد رشد افزایش صعود مثبت رونق بهبود جهش قوی موفق")]
    result = engine.analyze("فولاد", D, chunks)
    assert 0 <= result.score <= 100