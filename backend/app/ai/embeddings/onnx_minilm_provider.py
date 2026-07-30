"""Local, free embedding provider backed by ONNX Runtime.

Uses the same all-MiniLM-L6-v2 model as sentence-transformers, but through
ONNX Runtime instead of PyTorch. PyTorch's official wheels require AVX2,
which some older CPUs (e.g. pre-Haswell Intel chips) don't support, so
ONNX Runtime is the portable choice here — same model, no GPU/AVX2
requirement.
"""
from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

from app.ai.embeddings.base import EmbeddingProvider


class OnnxMiniLMEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str | None = None):
        # model_name kept for interface/config symmetry; this provider only
        # supports the bundled all-MiniLM-L6-v2 ONNX model.
        self._embedding_function = ONNXMiniLM_L6_V2()

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._embedding_function(texts)
        return [list(map(float, vector)) for vector in embeddings]
