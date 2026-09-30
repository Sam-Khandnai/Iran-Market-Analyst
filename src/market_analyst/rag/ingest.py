from market_analyst.data.db.session import get_session_factory
from market_analyst.rag.chunker import chunk_document
from market_analyst.rag.embeddings import Embedder
from market_analyst.rag.models import DocumentInput
from market_analyst.rag.store import VectorStore


async def ingest_documents(
    documents: list[DocumentInput], embedder: Embedder, session_factory=None,
) -> int:
    session_factory = session_factory or get_session_factory()
    total = 0
    async with session_factory() as session:
        store = VectorStore(session)
        for doc in documents:
            chunks = chunk_document(doc)
            if not chunks:
                continue
            embeddings = embedder.embed([c.text for c in chunks])
            await store.add_chunks(chunks, embeddings)
            total += len(chunks)
        await session.commit()
    return total