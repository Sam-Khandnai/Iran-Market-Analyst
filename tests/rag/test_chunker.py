from datetime import date

from market_analyst.rag.chunker import chunk_document
from market_analyst.rag.models import DocumentInput


def _doc(text: str, **overrides) -> DocumentInput:
    defaults = {
        "document_id": "doc1", "doc_type": "news", "source": "test-source",
        "symbol": "فولاد", "title": "خبر تستی", "published_at": date(2024, 1, 1), "text": text,
    }
    defaults.update(overrides)
    return DocumentInput(**defaults)


def test_short_text_produces_single_chunk():
    chunks = chunk_document(_doc("این یک متن کوتاه تستی است."), chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0].chunk_id == "doc1:0"


def test_long_text_splits_into_overlapping_chunks():
    text = " ".join(f"کلمه{i}" for i in range(300))
    chunks = chunk_document(_doc(text), chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(c.document_id == "doc1" for c in chunks)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_chunks_do_not_cut_mid_word():
    text = " ".join(f"واژه{i}" for i in range(50))
    chunks = chunk_document(_doc(text), chunk_size=30, overlap=5)
    for c in chunks:
        assert not c.text.startswith(" ")
        assert not c.text.endswith(" ")


def test_empty_text_produces_no_chunks():
    assert chunk_document(_doc("   ")) == []


def test_invalid_overlap_raises():
    import pytest
    with pytest.raises(ValueError):
        chunk_document(_doc("متن"), chunk_size=10, overlap=10)