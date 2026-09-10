from unittest.mock import Mock, patch

import numpy as np

from app.ai.embeddings.fastembed_provider import FastEmbedEmbeddingProvider


@patch("app.ai.embeddings.fastembed_provider.TextEmbedding")
def test_provider_uses_passage_and_query_paths(text_embedding: Mock, tmp_path):
    model = text_embedding.return_value
    model.passage_embed.return_value = iter([np.array([0.1, 0.2])])
    model.query_embed.return_value = iter([np.array([0.3, 0.4])])

    provider = FastEmbedEmbeddingProvider("model", cache_dir=tmp_path, threads=2)

    assert provider.embed(["document"]) == [[0.1, 0.2]]
    assert provider.embed_query("question") == [0.3, 0.4]
    text_embedding.assert_called_once_with(
        model_name="model",
        cache_dir=str(tmp_path),
        threads=2,
        providers=["CPUExecutionProvider"],
    )
    model.passage_embed.assert_called_once_with(["document"])
    model.query_embed.assert_called_once_with("question")


@patch("app.ai.embeddings.fastembed_provider.TextEmbedding")
def test_provider_does_not_call_model_for_empty_batch(text_embedding: Mock):
    provider = FastEmbedEmbeddingProvider("model")

    assert provider.embed([]) == []
    text_embedding.return_value.passage_embed.assert_not_called()
