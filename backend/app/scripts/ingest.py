"""Embed chunks.jsonl and load them into ChromaDB.

Usage:
    python -m app.scripts.ingest
    python -m app.scripts.ingest --resume
    python -m app.scripts.ingest --resume --batch-delay-seconds 65

This is a full rebuild of the (derived) vector index — safe to re-run any
time, since it never touches the raw PDFs or metadata.csv, only the
derived data/processed and data/chroma directories.
"""
import argparse
import json
import sys
import time

from app.ai.embeddings.factory import build_embedding_provider
from app.config.settings import get_settings
from app.core.logging import configure_logging, get_logger
from app.data.chroma_repository import ChromaRepository
from app.data.metadata_repository import MetadataRepository

logger = get_logger(__name__)

_BATCH_SIZE = 64


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Embed processed chunks into ChromaDB.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Keep the collection and skip chunk IDs that are already indexed.",
    )
    parser.add_argument(
        "--batch-delay-seconds",
        type=float,
        default=0,
        help="Wait between successful batches (useful for hosted free-tier rate limits).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=_BATCH_SIZE,
        help="Number of chunks per embedding request.",
    )
    return parser.parse_args()


def load_chunks(processed_dir) -> list[dict]:
    chunks_path = processed_dir / "chunks.jsonl"
    if not chunks_path.exists():
        return []
    with chunks_path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
    args = parse_args()
    if args.batch_size < 1:
        raise ValueError("--batch-size must be at least 1")
    settings = get_settings()
    configure_logging(settings.log_level)

    chunks = load_chunks(settings.processed_dir)
    if not chunks:
        logger.error("No chunks found. Run `python -m app.scripts.build_chunks` first.")
        sys.exit(1)

    documents_by_id = {doc.document_id: doc for doc in MetadataRepository(settings.metadata_csv_path).load_all()}
    if not documents_by_id:
        logger.error("metadata.csv is empty. Run `python -m app.scripts.build_metadata` first.")
        sys.exit(1)

    embedding_provider = build_embedding_provider(settings)
    chroma_repo = ChromaRepository(settings.chroma_persist_dir, settings.chroma_collection_name)
    if args.resume:
        logger.info("Resuming ingestion with %d chunks already indexed", chroma_repo.count())
    else:
        chroma_repo.reset()

    total = chroma_repo.count()
    for batch_start in range(0, len(chunks), args.batch_size):
        batch = chunks[batch_start : batch_start + args.batch_size]
        existing_ids = chroma_repo.existing_ids([chunk["chunk_id"] for chunk in batch]) if args.resume else set()

        ids, texts, metadatas = [], [], []
        for chunk in batch:
            if chunk["chunk_id"] in existing_ids:
                continue
            doc = documents_by_id.get(chunk["document_id"])
            if doc is None:
                logger.warning("Chunk %s references unknown document_id; skipping", chunk["chunk_id"])
                continue
            ids.append(chunk["chunk_id"])
            texts.append(chunk["text"])
            metadatas.append(
                {
                    "document_id": doc.document_id,
                    "title": doc.title,
                    "author": doc.author,
                    "era": doc.era,
                    "source_type": doc.source_type,
                }
            )

        if not ids:
            continue

        embeddings = embedding_provider.embed(texts)
        chroma_repo.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
        total += len(ids)
        logger.info("Ingested %d/%d chunks", total, len(chunks))
        if args.batch_delay_seconds > 0 and total < len(chunks):
            logger.info(
                "Waiting %.1f seconds before the next embedding batch",
                args.batch_delay_seconds,
            )
            time.sleep(args.batch_delay_seconds)

    logger.info("Ingestion complete: %d chunks in collection %r", total, settings.chroma_collection_name)


if __name__ == "__main__":
    main()
