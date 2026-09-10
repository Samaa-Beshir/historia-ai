from unittest.mock import Mock, patch

import pytest

from app.ai.embeddings.factory import build_embedding_provider
from app.ai.embeddings.onnx_minilm_provider import OnnxMiniLMEmbeddingProvider
from app.config.settings import Settings
from app.core.exceptions import ConfigurationError


def test_factory_builds_default_onnx_provider():
    provider = build_embedding_provider(Settings())

    assert isinstance(provider, OnnxMiniLMEmbeddingProvider)


@patch("app.ai.embeddings.fastembed_provider.FastEmbedEmbeddingProvider")
def test_factory_passes_multilingual_settings(provider_class: Mock, tmp_path):
    settings = Settings(
        embedding_provider="fastembed",
        embedding_model_name="multilingual-model",
        embedding_cache_dir=tmp_path,
        embedding_threads=2,
    )

    build_embedding_provider(settings)

    provider_class.assert_called_once_with(
        model_name="multilingual-model",
        cache_dir=tmp_path,
        threads=2,
    )


def test_factory_rejects_unknown_provider():
    with pytest.raises(ConfigurationError, match="Unsupported embedding provider"):
        build_embedding_provider(Settings(embedding_provider="unknown"))


def test_factory_requires_key_for_gemini_embeddings():
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        build_embedding_provider(Settings(embedding_provider="gemini", gemini_api_key=None))
