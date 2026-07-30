"""Top-K semantic retrieval over ChromaDB.

Architecture rule: retrieval always precedes generation. The chat service
never calls the LLM without going through this class first.
"""
from app.ai.embeddings.base import EmbeddingProvider
from app.ai.retrieval.models import RetrievedChunk
from app.core.exceptions import RetrievalError
from app.core.logging import get_logger
from app.data.chroma_repository import ChromaRepository

logger = get_logger(__name__)


class Retriever:
    def __init__(self, chroma_repository: ChromaRepository, embedding_provider: EmbeddingProvider):
        self._chroma = chroma_repository
        self._embeddings = embedding_provider

    def retrieve(self, query: str, top_k: int, era: str | None = None) -> list[RetrievedChunk]:
        try:
            query_embedding = self._embeddings.embed_query(query)
            where = {"era": era} if era else None
            result = self._chroma.query(query_embedding, top_k=top_k, where=where)
        except Exception as exc:
            raise RetrievalError(f"Retrieval failed: {exc}") from exc

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        chunks = [
            RetrievedChunk(
                chunk_id=chunk_id,
                document_id=metadata["document_id"],
                text=document,
                title=metadata["title"],
                author=metadata["author"],
                era=metadata["era"],
                source_type=metadata["source_type"],
                distance=distance,
            )
            for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances)
        ]
        logger.info("Retrieved %d chunks for query (era=%s)", len(chunks), era)
        return chunks
