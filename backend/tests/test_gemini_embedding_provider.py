from unittest.mock import Mock, call, patch

import pytest

from app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider


def make_response(payload: dict, status_code: int = 200) -> Mock:
    response = Mock(status_code=status_code, is_success=status_code < 400)
    response.json.return_value = payload
    return response


def make_provider(client_class: Mock) -> tuple[GeminiEmbeddingProvider, Mock]:
    client = client_class.return_value
    provider = GeminiEmbeddingProvider(
        api_key="test-key",
        model_name="gemini-embedding-001",
        output_dimensionality=768,
        document_task_type="RETRIEVAL_DOCUMENT",
        query_task_type="QUESTION_ANSWERING",
        request_timeout_seconds=30,
        max_retries=2,
    )
    return provider, client


@patch("app.ai.embeddings.gemini_provider.httpx.Client")
def test_provider_uses_distinct_document_and_query_tasks(client_class):
    provider, client = make_provider(client_class)
    client.post.side_effect = [
        make_response({"embeddings": [{"values": [3.0, 4.0]}, {"values": [0.0, 2.0]}]}),
        make_response({"embedding": {"values": [5.0, 12.0]}}),
    ]

    assert provider.embed(["first", "second"]) == [
        [0.6000000238418579, 0.800000011920929],
        [0.0, 1.0],
    ]
    assert provider.embed_query("question") == pytest.approx([5 / 13, 12 / 13])
    client_class.assert_called_once_with(
        base_url="https://generativelanguage.googleapis.com/v1beta",
        headers={"x-goog-api-key": "test-key"},
        timeout=30,
    )
    assert client.post.call_args_list == [
        call(
            "/models/gemini-embedding-001:batchEmbedContents",
            json={
                "requests": [
                    {
                        "model": "models/gemini-embedding-001",
                        "content": {"parts": [{"text": "first"}]},
                        "taskType": "RETRIEVAL_DOCUMENT",
                        "outputDimensionality": 768,
                    },
                    {
                        "model": "models/gemini-embedding-001",
                        "content": {"parts": [{"text": "second"}]},
                        "taskType": "RETRIEVAL_DOCUMENT",
                        "outputDimensionality": 768,
                    },
                ]
            },
        ),
        call(
            "/models/gemini-embedding-001:embedContent",
            json={
                "content": {"parts": [{"text": "question"}]},
                "taskType": "QUESTION_ANSWERING",
                "outputDimensionality": 768,
            },
        ),
    ]


@patch("app.ai.embeddings.gemini_provider.time.sleep")
@patch("app.ai.embeddings.gemini_provider.httpx.Client")
def test_provider_retries_rate_limit(client_class, sleep):
    provider, client = make_provider(client_class)
    client.post.side_effect = [
        make_response({"error": {"status": "RESOURCE_EXHAUSTED"}}, 429),
        make_response({"embedding": {"values": [1.0, 0.0]}}),
    ]

    assert provider.embed_query("question") == [1.0, 0.0]
    sleep.assert_called_once_with(1)


@patch("app.ai.embeddings.gemini_provider.httpx.Client")
def test_provider_rejects_zero_vector(client_class):
    provider, client = make_provider(client_class)
    client.post.return_value = make_response({"embedding": {"values": [0.0, 0.0]}})

    with pytest.raises(ValueError, match="zero vector"):
        provider.embed_query("question")
