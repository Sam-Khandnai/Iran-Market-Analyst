
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from market_analyst.data.db.tables import DocumentChunkRow
from market_analyst.rag.models import Chunk, RetrievedChunk
from market_analyst.rag.similarity import cosine_similarity

_CANDIDATE_LIMIT = 2000


class VectorStore:
    def __init__(self, session: AsyncSession):
        self.s = session

    async def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        for chunk, emb in zip(chunks, embeddings, strict=True):
            values = {
                "chunk_id": chunk.chunk_id, "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index, "doc_type": chunk.doc_type,
                "source": chunk.source, "symbol": chunk.symbol, "title": chunk.title,
                "published_at": chunk.published_at, "text": chunk.text, "embedding": emb,
            }
            stmt = insert(DocumentChunkRow).values(values)
            stmt = stmt.on_conflict_do_update(
                index_elements=["document_id", "chunk_index"],
                set_={k: v for k, v in values.items() if k not in ("document_id", "chunk_index")},
            )
            await self.s.execute(stmt)

    async def search(
        self,
        query_embedding: list[float],
        doc_type: str | None = None,
        symbol: str | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        q = select(DocumentChunkRow)
        if doc_type is not None:
            q = q.where(DocumentChunkRow.doc_type == doc_type)
        if symbol is not None:
            q = q.where(DocumentChunkRow.symbol == symbol)
        q = q.limit(_CANDIDATE_LIMIT)
        rows = (await self.s.execute(q)).scalars().all()

        scored: list[RetrievedChunk] = []
        for row in rows:
            score = cosine_similarity(query_embedding, row.embedding)
            chunk = Chunk(
                chunk_id=row.chunk_id, document_id=row.document_id, chunk_index=row.chunk_index,
                doc_type=row.doc_type, source=row.source, symbol=row.symbol, title=row.title,
                published_at=row.published_at, text=row.text,
            )
            scored.append(RetrievedChunk(chunk=chunk, score=score))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]