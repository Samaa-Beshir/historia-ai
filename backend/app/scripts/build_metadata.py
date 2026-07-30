"""Build data/metadata.csv from the raw document tree.

Usage:
    python -m app.scripts.build_metadata

Walks <raw_books_dir>/<books|research_papers>/<Era>/*.pdf and writes one
metadata row per PDF. Title/author come from the PDF's own internal
metadata, falling back to the first line of extracted text — never from
the filename (CLAUDE.md: "Never read metadata from filenames"). Era and
source_type come from directory placement, which is dataset organization,
not filename parsing. The raw PDFs themselves are only ever read, never
modified.
"""
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

from app.config.settings import get_settings
from app.core.logging import configure_logging, get_logger
from app.data.metadata_repository import MetadataRepository
from app.data.models import DocumentMetadata

logger = get_logger(__name__)

_NAMESPACE = uuid.UUID("6f6f2a2e-6f0e-4c1a-9d2b-2c9a5f6e1a10")
_SOURCE_TYPE_MAP = {
    "books": "book",
    "research_papers": "research_paper",
}


def _era_from_folder(folder_name: str) -> str:
    return folder_name.replace("_", " ").strip()


def _extract_title_author(reader: PdfReader, fallback_stem: str) -> tuple[str, str]:
    info = reader.metadata
    title = (info.title or "").strip() if info else ""
    author = (info.author or "").strip() if info else ""

    if not title:
        try:
            first_page_text = reader.pages[0].extract_text() or ""
        except Exception:
            first_page_text = ""
        for line in first_page_text.splitlines():
            candidate = line.strip()
            if len(candidate) >= 4:
                title = candidate
                break

    if not title:
        title = f"Untitled document ({fallback_stem[:8]})"
    if not author:
        author = "Unknown"

    return title, author


def build_metadata() -> list[DocumentMetadata]:
    settings = get_settings()
    raw_dir = settings.raw_books_dir
    records: list[DocumentMetadata] = []

    for source_folder, source_type in _SOURCE_TYPE_MAP.items():
        base = raw_dir / source_folder
        if not base.is_dir():
            continue

        for era_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            era = _era_from_folder(era_dir.name)

            for pdf_path in sorted(era_dir.glob("*.pdf")):
                relative_path = pdf_path.relative_to(raw_dir).as_posix()
                document_id = str(uuid.uuid5(_NAMESPACE, relative_path))

                try:
                    reader = PdfReader(str(pdf_path))
                    page_count = len(reader.pages)
                    title, author = _extract_title_author(reader, document_id)
                except Exception as exc:
                    logger.warning("Failed to read %s: %s", pdf_path, exc)
                    page_count = 0
                    title, author = f"Unreadable document ({document_id[:8]})", "Unknown"

                records.append(
                    DocumentMetadata(
                        document_id=document_id,
                        filename=pdf_path.name,
                        relative_path=relative_path,
                        era=era,
                        source_type=source_type,
                        title=title,
                        author=author,
                        page_count=page_count,
                        created_at=datetime.now(timezone.utc),
                    )
                )
                logger.info("Indexed %s -> era=%s title=%r", relative_path, era, title)

    return records


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    records = build_metadata()
    if not records:
        logger.error("No PDFs found under %s", settings.raw_books_dir)
        sys.exit(1)

    MetadataRepository(settings.metadata_csv_path).save_all(records)
    logger.info("Wrote %d records to %s", len(records), settings.metadata_csv_path)


if __name__ == "__main__":
    main()
