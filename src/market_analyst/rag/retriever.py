from market_analyst.data.db.session import get_session_factory
from market_analyst.logging import get_logger
from market_analyst.rag.embeddings import Embedder, HashingEmbedder
from market_analyst.rag.models import RetrievedChunk
from market_analyst.rag.store import VectorStore

log = get_logger("rag.retriever")


class Retriever:
    def __init__(self, embedder: Embedder, session_factory=None):
        self._embedder = embedder
        self._session_factory = session_factory or get_session_factory()

    async def retrieve(
        self,
        query: str,
        doc_type: str | None = None,
        symbol: str | None = None,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """هرگز پایپ‌لاین را کرش نمی‌دهد؛ در صورت خطای DB/زیرساخت لیست خالی برمی‌گرداند."""
        try:
            [query_embedding] = self._embedder.embed([query])
            async with self._session_factory() as session:
                store = VectorStore(session)
                return await store.search(
                    query_embedding,
                    doc_type=doc_type,
                    symbol=symbol,
                    top_k=top_k,
                )
        except Exception as e:  # noqa: BLE001
            log.warning(
                "retrieval_failed",
                error=str(e),
                query=query)
            return []


def build_default_retriever() -> Retriever:
    return Retriever(embedder=HashingEmbedder())