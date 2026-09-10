"""Multilingual embeddings backed by FastEmbed and ONNX Runtime."""
from pathlib import Path

from fastembed import TextEmbedding

from app.ai.embeddings.base import EmbeddingProvider


class FastEmbedEmbeddingProvider(EmbeddingProvider):
    """Run a FastEmbed-supported model without a PyTorch dependency."""

    def __init__(
        self,
        model_name: str,
        cache_dir: Path | None = None,
        threads: int | None = None,
    ):
        self._embedding_model = TextEmbedding(
            model_name=model_name,
            cache_dir=str(cache_dir) if cache_dir else None,
            threads=threads,
            providers=["CPUExecutionProvider"],
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return [vector.astype(float).tolist() for vector in self._embedding_model.passage_embed(texts)]

    def embed_query(self, text: str) -> list[float]:
        vector = next(iter(self._embedding_model.query_embed(text)))
        return vector.astype(float).tolist()
