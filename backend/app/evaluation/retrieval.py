"""Language-aware evaluation for the retrieval stage of the RAG pipeline.

The evaluator deliberately stops before prompt construction and generation so
embedding and retrieval changes can be compared without LLM variability or
API cost.
"""
import json
from collections import defaultdict
from pathlib import Path
from typing import Literal, Protocol

from pydantic import BaseModel, Field

from app.ai.retrieval.models import RetrievedChunk


class RetrieverProtocol(Protocol):
    def retrieve(self, query: str, top_k: int, era: str | None = None) -> list[RetrievedChunk]: ...


class RetrievalEvaluationCase(BaseModel):
    case_id: str
    pair_id: str
    language: Literal["ar", "en"]
    question: str = Field(min_length=1)
    expected_document_ids: list[str] = Field(min_length=1)
    era: str | None = None


class RetrievalCaseResult(BaseModel):
    case_id: str
    pair_id: str
    language: Literal["ar", "en"]
    first_relevant_rank: int | None
    reciprocal_rank: float
    retrieved_document_ids: list[str]


class RetrievalMetrics(BaseModel):
    cases: int
    hits: int
    hit_rate: float
    mean_reciprocal_rank: float


class RetrievalEvaluationSummary(BaseModel):
    top_k: int
    overall: RetrievalMetrics
    by_language: dict[str, RetrievalMetrics]
    results: list[RetrievalCaseResult]


def load_evaluation_cases(path: Path) -> list[RetrievalEvaluationCase]:
    """Load and validate one JSON object per line from an evaluation dataset."""
    cases: list[RetrievalEvaluationCase] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                cases.append(RetrievalEvaluationCase.model_validate(json.loads(line)))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"Invalid evaluation case at {path}:{line_number}: {exc}") from exc
    if not cases:
        raise ValueError(f"Evaluation dataset is empty: {path}")
    return cases


def _calculate_metrics(results: list[RetrievalCaseResult]) -> RetrievalMetrics:
    hits = sum(result.first_relevant_rank is not None for result in results)
    return RetrievalMetrics(
        cases=len(results),
        hits=hits,
        hit_rate=round(hits / len(results), 4),
        mean_reciprocal_rank=round(sum(result.reciprocal_rank for result in results) / len(results), 4),
    )


def evaluate_retriever(
    retriever: RetrieverProtocol,
    cases: list[RetrievalEvaluationCase],
    top_k: int,
) -> RetrievalEvaluationSummary:
    """Measure Hit@K and MRR overall and separately for Arabic and English."""
    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    results: list[RetrievalCaseResult] = []
    for case in cases:
        chunks = retriever.retrieve(query=case.question, top_k=top_k, era=case.era)
        retrieved_ids = [chunk.document_id for chunk in chunks]
        expected_ids = set(case.expected_document_ids)
        first_relevant_rank = next(
            (rank for rank, document_id in enumerate(retrieved_ids, start=1) if document_id in expected_ids),
            None,
        )
        results.append(
            RetrievalCaseResult(
                case_id=case.case_id,
                pair_id=case.pair_id,
                language=case.language,
                first_relevant_rank=first_relevant_rank,
                reciprocal_rank=round(1 / first_relevant_rank, 4) if first_relevant_rank else 0.0,
                retrieved_document_ids=retrieved_ids,
            )
        )

    grouped: dict[str, list[RetrievalCaseResult]] = defaultdict(list)
    for result in results:
        grouped[result.language].append(result)

    return RetrievalEvaluationSummary(
        top_k=top_k,
        overall=_calculate_metrics(results),
        by_language={language: _calculate_metrics(items) for language, items in sorted(grouped.items())},
        results=results,
    )
