"""Embedding provider abstraction.

Swappable so the vector representation can change (local model, hosted
API, etc.) without touching retrieval or ingestion code.
"""
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Embed a batch of texts, e.g. document chunks at ingestion time."""

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return self.embed([text])[0]
