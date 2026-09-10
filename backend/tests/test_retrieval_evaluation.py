import json

import pytest

from app.ai.retrieval.models import RetrievedChunk
from app.evaluation.retrieval import evaluate_retriever, load_evaluation_cases


def make_chunk(document_id: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=f"{document_id}::0",
        document_id=document_id,
        text="Historical text",
        title="Source",
        author="Historian",
        era="Modern Egypt",
        source_type="book",
        distance=0.2,
    )


class StubRetriever:
    def retrieve(self, query: str, top_k: int, era: str | None = None) -> list[RetrievedChunk]:
        ids = {
            "english question": ["wrong", "target"],
            "سؤال عربي": ["target", "wrong"],
        }[query]
        return [make_chunk(document_id) for document_id in ids[:top_k]]


def test_evaluate_retriever_reports_metrics_by_language():
    cases = [
        {
            "case_id": "en-1",
            "pair_id": "pair-1",
            "language": "en",
            "question": "english question",
            "expected_document_ids": ["target"],
        },
        {
            "case_id": "ar-1",
            "pair_id": "pair-1",
            "language": "ar",
            "question": "سؤال عربي",
            "expected_document_ids": ["target"],
        },
    ]

    from app.evaluation.retrieval import RetrievalEvaluationCase

    summary = evaluate_retriever(StubRetriever(), [RetrievalEvaluationCase(**case) for case in cases], top_k=2)

    assert summary.overall.hit_rate == 1.0
    assert summary.overall.mean_reciprocal_rank == 0.75
    assert summary.by_language["en"].mean_reciprocal_rank == 0.5
    assert summary.by_language["ar"].mean_reciprocal_rank == 1.0


def test_load_evaluation_cases_reports_invalid_line(tmp_path):
    dataset = tmp_path / "cases.jsonl"
    dataset.write_text(json.dumps({"case_id": "missing-fields"}) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="cases.jsonl:1"):
        load_evaluation_cases(dataset)


def test_evaluate_retriever_rejects_invalid_top_k():
    with pytest.raises(ValueError, match="top_k"):
        evaluate_retriever(StubRetriever(), [], top_k=0)
