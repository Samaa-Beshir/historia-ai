"""Construct the configured embedding provider in one place."""
from app.ai.embeddings.base import EmbeddingProvider
from app.config.settings import Settings
from app.core.exceptions import ConfigurationError


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    provider = settings.embedding_provider.lower()
    if provider == "onnx_minilm":
        from app.ai.embeddings.onnx_minilm_provider import OnnxMiniLMEmbeddingProvider

        return OnnxMiniLMEmbeddingProvider(settings.embedding_model_name)
    if provider == "fastembed":
        from app.ai.embeddings.fastembed_provider import FastEmbedEmbeddingProvider

        return FastEmbedEmbeddingProvider(
            model_name=settings.embedding_model_name,
            cache_dir=settings.embedding_cache_dir,
            threads=settings.embedding_threads,
        )
    if provider == "gemini":
        from app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider

        if settings.gemini_api_key is None:
            raise ConfigurationError(
                "GEMINI_API_KEY is required when EMBEDDING_PROVIDER is 'gemini'."
            )
        return GeminiEmbeddingProvider(
            api_key=settings.gemini_api_key.get_secret_value(),
            model_name=settings.embedding_model_name,
            output_dimensionality=settings.embedding_output_dimensionality,
            document_task_type=settings.embedding_document_task_type,
            query_task_type=settings.embedding_query_task_type,
            request_timeout_seconds=settings.embedding_request_timeout_seconds,
            max_retries=settings.embedding_max_retries,
            rate_limit_retry_seconds=settings.embedding_rate_limit_retry_seconds,
        )
    raise ConfigurationError(
        f"Unsupported embedding provider {settings.embedding_provider!r}. "
        "Choose 'onnx_minilm', 'fastembed', or 'gemini'."
    )
