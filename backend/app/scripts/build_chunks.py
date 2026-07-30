"""Build data/processed/chunks.jsonl from the raw PDFs listed in
metadata.csv.

Usage:
    python -m app.scripts.build_chunks

Reads metadata.csv (authoritative document catalog), extracts and cleans
text from each raw PDF (read-only), and writes overlapping chunks. Each
chunk carries only cleaned text plus a document_id — no metadata is
duplicated into chunk content (DATA_PIPELINE.md).
"""
import json
import sys

from app.config.settings import get_settings
from app.core.logging import configure_logging, get_logger
from app.data.metadata_repository import MetadataRepository
from app.scripts.text_processing import chunk_text, clean_text, extract_pdf_text

logger = get_logger(__name__)


def build_chunks() -> int:
    settings = get_settings()
    metadata_repo = MetadataRepository(settings.metadata_csv_path)
    documents = metadata_repo.load_all()

    if not documents:
        logger.error("metadata.csv is empty. Run `python -m app.scripts.build_metadata` first.")
        return 0

    settings.processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = settings.processed_dir / "chunks.jsonl"
    total_chunks = 0

    with output_path.open("w", encoding="utf-8") as out:
        for doc in documents:
            pdf_path = settings.raw_books_dir / doc.relative_path
            try:
                raw_text = extract_pdf_text(str(pdf_path))
            except Exception as exc:
                logger.warning("Skipping %s: failed to extract text (%s)", doc.relative_path, exc)
                continue

            cleaned = clean_text(raw_text)
            pieces = chunk_text(cleaned, settings.chunk_size_chars, settings.chunk_overlap_chars)

            for index, piece in enumerate(pieces):
                record = {
                    "chunk_id": f"{doc.document_id}::{index}",
                    "document_id": doc.document_id,
                    "chunk_index": index,
                    "text": piece,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

            logger.info("Chunked %s -> %d chunks", doc.relative_path, len(pieces))

    logger.info("Wrote %d chunks to %s", total_chunks, output_path)
    return total_chunks


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    total = build_chunks()
    if total == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
