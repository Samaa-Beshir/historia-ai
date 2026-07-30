"""Repository for data/metadata.csv — the authoritative document catalog.

DATA_PIPELINE.md: "metadata.csv is authoritative." Nothing downstream
should re-derive era/title/author from a filename; it reads them here.
"""
import csv
from pathlib import Path

from app.core.exceptions import NotFoundError
from app.data.models import DocumentMetadata

_FIELDNAMES = [
    "document_id",
    "filename",
    "relative_path",
    "era",
    "source_type",
    "title",
    "author",
    "page_count",
    "created_at",
]


class MetadataRepository:
    def __init__(self, csv_path: Path):
        self._csv_path = csv_path

    def save_all(self, records: list[DocumentMetadata]) -> None:
        self._csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self._csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
            writer.writeheader()
            for record in records:
                row = record.model_dump()
                row["created_at"] = record.created_at.isoformat()
                writer.writerow(row)

    def load_all(self) -> list[DocumentMetadata]:
        if not self._csv_path.exists():
            return []
        with self._csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [DocumentMetadata(**row) for row in reader]

    def get(self, document_id: str) -> DocumentMetadata:
        for record in self.load_all():
            if record.document_id == document_id:
                return record
        raise NotFoundError(f"No metadata for document_id={document_id!r}")

    def list_eras(self) -> list[str]:
        seen: dict[str, None] = {}
        for record in self.load_all():
            seen.setdefault(record.era, None)
        return list(seen.keys())

    def filter(self, era: str | None = None, source_type: str | None = None) -> list[DocumentMetadata]:
        records = self.load_all()
        if era is not None:
            records = [r for r in records if r.era == era]
        if source_type is not None:
            records = [r for r in records if r.source_type == source_type]
        return records
