"""Hosted multilingual embeddings using the Gemini API."""
import time

import httpx
import numpy as np

from app.ai.embeddings.base import EmbeddingProvider


class GeminiEmbeddingProvider(EmbeddingProvider):
    """Create retrieval embeddings without loading a local transformer."""

    def __init__(
        self,
        api_key: str,
        model_name: str,
        output_dimensionality: int,
        document_task_type: str,
        query_task_type: str,
        request_timeout_seconds: float,
        max_retries: int,
        rate_limit_retry_seconds: float,
    ):
        self._model_name = model_name.removeprefix("models/")
        self._qualified_model_name = f"models/{self._model_name}"
        self._output_dimensionality = output_dimensionality
        self._document_task_type = document_task_type
        self._query_task_type = query_task_type
        self._max_retries = max_retries
        self._rate_limit_retry_seconds = rate_limit_retry_seconds
        self._client = httpx.Client(
            base_url="https://generativelanguage.googleapis.com/v1beta",
            headers={"x-goog-api-key": api_key},
            timeout=request_timeout_seconds,
        )

    def _request(self, endpoint: str, payload: dict) -> dict:
        for attempt in range(self._max_retries + 1):
            response = self._client.post(endpoint, json=payload)
            retryable = response.status_code == 429 or response.status_code >= 500
            if retryable and attempt < self._max_retries:
                delay = self._rate_limit_retry_seconds if response.status_code == 429 else 2**attempt
                time.sleep(delay)
                continue
            if not response.is_success:
                try:
                    reason = response.json().get("error", {}).get("status", "unknown")
                except ValueError:
                    reason = "unknown"
                raise RuntimeError(
                    f"Gemini embedding request failed with HTTP {response.status_code} ({reason})"
                )
            return response.json()
        raise RuntimeError("Gemini embedding request exhausted its retries")

    def _normalize(self, vector: list[float]) -> list[float]:
        values = np.asarray(vector, dtype=np.float32)
        magnitude = np.linalg.norm(values)
        if magnitude == 0:
            raise ValueError("Embedding provider returned a zero vector")
        return (values / magnitude).astype(float).tolist()

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        requests = [
            {
                "model": self._qualified_model_name,
                "content": {"parts": [{"text": text}]},
                "taskType": self._document_task_type,
                "outputDimensionality": self._output_dimensionality,
            }
            for text in texts
        ]
        response = self._request(
            f"/models/{self._model_name}:batchEmbedContents",
            {"requests": requests},
        )
        vectors = [embedding["values"] for embedding in response["embeddings"]]
        if len(vectors) != len(texts):
            raise ValueError(
                f"Embedding provider returned {len(vectors)} vectors for {len(texts)} texts"
            )
        return [self._normalize(vector) for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        response = self._request(
            f"/models/{self._model_name}:embedContent",
            {
                "content": {"parts": [{"text": text}]},
                "taskType": self._query_task_type,
                "outputDimensionality": self._output_dimensionality,
            },
        )
        return self._normalize(response["embedding"]["values"])
