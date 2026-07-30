"""Repository wrapping the ChromaDB persistent collection.

Every other layer talks to Chroma exclusively through this class, so the
vector store can be swapped without touching retrieval/service code.
"""
from pathlib import Path
from typing import Any

import chromadb


class ChromaRepository:
    def __init__(self, persist_dir: Path, collection_name: str):
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self._collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)

    def query(
        self,
        query_embedding: list[float],
        top_k: int,
        where: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        """Delete and recreate the collection. Used only by the ingestion script."""
        name = self._collection.name
        self._client.delete_collection(name)
        self._collection = self._client.get_or_create_collection(
            name=name,
            metadata={"hnsw:space": "cosine"},
        )
