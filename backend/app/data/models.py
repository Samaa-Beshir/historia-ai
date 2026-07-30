"""Data-layer record types, independent of any web/API concerns."""
from datetime import datetime

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """One row of metadata.csv — the single source of truth for a document.

    Never derived from filenames at query time; built once by the ingestion
    pipeline from PDF content/internal metadata and directory placement.
    """

    document_id: str
    filename: str
    relative_path: str
    era: str
    source_type: str  # "book" | "research_paper"
    title: str
    author: str
    page_count: int
    created_at: datetime


class Chunk(BaseModel):
    """A single cleaned text chunk, linked back to its document by id only."""

    chunk_id: str
    document_id: str
    chunk_index: int
    text: str
