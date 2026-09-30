from market_analyst.rag.models import Chunk, DocumentInput


def chunk_document(doc: DocumentInput, chunk_size: int = 500, overlap: int = 50) -> list[Chunk]:
    """تقسیم متن به قطعات هم‌پوشان با برش روی نزدیک‌ترین فاصله (نه وسط کلمه)."""
    text = doc.text.strip()
    if not text:
        return []
    if chunk_size <= overlap:
        raise ValueError("chunk_size باید بزرگ‌تر از overlap باشد")

    chunks: list[Chunk] = []
    start = 0
    index = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            space = text.rfind(" ", start, end)
            if space > start:
                end = space
        piece = text[start:end].strip()
        if piece:
            chunks.append(Chunk(
                chunk_id=f"{doc.document_id}:{index}",
                document_id=doc.document_id,
                chunk_index=index,
                doc_type=doc.doc_type,
                source=doc.source,
                symbol=doc.symbol,
                title=doc.title,
                published_at=doc.published_at,
                text=piece,
            ))
            index += 1
        if end >= n:
            break
        start = max(end - overlap, start + 1)
    return chunks