"""Embed chunks.jsonl and load them into ChromaDB.

Usage:
    python -m app.scripts.ingest

This is a full rebuild of the (derived) vector index — safe to re-run any
time, since it never touches the raw PDFs or metadata.csv, only the
derived data/processed and data/chroma directories.
"""
import json
import sys

from app.ai.embeddings.onnx_minilm_provider import OnnxMiniLMEmbeddingProvider
from app.config.settings import get_settings
from app.core.logging import configure_logging, get_logger
from app.data.chroma_repository import ChromaRepository
from app.data.metadata_repository import MetadataRepository

logger = get_logger(__name__)

_BATCH_SIZE = 64


def load_chunks(processed_dir) -> list[dict]:
    chunks_path = processed_dir / "chunks.jsonl"
    if not chunks_path.exists():
        return []
    with chunks_path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main() -> None:
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

    embedding_provider = OnnxMiniLMEmbeddingProvider(settings.embedding_model_name)
    chroma_repo = ChromaRepository(settings.chroma_persist_dir, settings.chroma_collection_name)
    chroma_repo.reset()

    total = 0
    for batch_start in range(0, len(chunks), _BATCH_SIZE):
        batch = chunks[batch_start : batch_start + _BATCH_SIZE]

        ids, texts, metadatas = [], [], []
        for chunk in batch:
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

    logger.info("Ingestion complete: %d chunks in collection %r", total, settings.chroma_collection_name)


if __name__ == "__main__":
    main()
