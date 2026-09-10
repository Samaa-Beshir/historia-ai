"""Run the bilingual retrieval baseline against the configured Chroma index.

Usage:
    python -m app.scripts.evaluate_retrieval
    python -m app.scripts.evaluate_retrieval --top-k 10 --include-cases
"""
import argparse
from pathlib import Path

from app.ai.embeddings.factory import build_embedding_provider
from app.ai.retrieval.retriever import Retriever
from app.config.settings import BACKEND_DIR, get_settings
from app.data.chroma_repository import ChromaRepository
from app.evaluation.retrieval import evaluate_retriever, load_evaluation_cases

DEFAULT_DATASET = BACKEND_DIR / "evaluation" / "bilingual_retrieval_v1.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate bilingual semantic retrieval.")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--include-cases", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()

    chroma = ChromaRepository(settings.chroma_persist_dir, settings.chroma_collection_name)
    embeddings = build_embedding_provider(settings)
    retriever = Retriever(chroma, embeddings)
    summary = evaluate_retriever(retriever, load_evaluation_cases(args.dataset), args.top_k)

    excluded_fields = None if args.include_cases else {"results"}
    print(summary.model_dump_json(indent=2, exclude=excluded_fields))


if __name__ == "__main__":
    main()
