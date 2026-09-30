import asyncio
from datetime import date

from market_analyst.data.db.session import init_db
from market_analyst.rag.embeddings import HashingEmbedder
from market_analyst.rag.ingest import ingest_documents
from market_analyst.rag.models import DocumentInput
from market_analyst.rag.retriever import Retriever


SAMPLE_DOCS = [
    DocumentInput(
        document_id="news-1", doc_type="news", source="خبرگزاری فرضی",
        symbol="فولاد", title="رشد سود فولاد مبارکه",
        published_at=date(2024, 6, 1),
        text="شرکت فولاد مبارکه اصفهان در گزارش سه‌ماهه اخیر خود از رشد چشمگیر سود و افزایش تولید خبر داد.",
    ),
    DocumentInput(
        document_id="news-2", doc_type="news", source="خبرگزاری فرضی",
        symbol="فولاد", title="کاهش صادرات فولاد",
        published_at=date(2024, 6, 5),
        text="به دلیل تحریم‌های جدید، صادرات فولاد مبارکه با کاهش قابل توجهی مواجه شده است.",
    ),
    DocumentInput(
        document_id="report-1", doc_type="financial_report", source="کدال",
        symbol="فولاد", title="گزارش فصلی",
        text="حاشیه سود عملیاتی فولاد مبارکه در فصل اخیر به دلیل افزایش هزینه انرژی تحت فشار قرار گرفت.",
    ),
]


async def main() -> None:
    await init_db()
    embedder = HashingEmbedder()

    n = await ingest_documents(SAMPLE_DOCS, embedder)
    print(f"تعداد چانک‌های ذخیره‌شده: {n}")

    retriever = Retriever(embedder)
    results = await retriever.retrieve("فولاد", doc_type="news", symbol="فولاد", top_k=5)
    for r in results:
        print(f"score={r.score:.3f} | {r.chunk.title} | {r.chunk.text[:60]}")


if __name__ == "__main__":
    asyncio.run(main())
