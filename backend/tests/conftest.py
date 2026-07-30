import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app.ai.retrieval.models import RetrievedChunk
from app.data.models import DocumentMetadata


@pytest.fixture
def sample_document() -> DocumentMetadata:
    return DocumentMetadata(
        document_id="doc-1",
        filename="ancient_001.pdf",
        relative_path="books/Ancient_Egypt/ancient_001.pdf",
        era="Ancient Egypt",
        source_type="book",
        title="The Old Kingdom",
        author="J. Historian",
        page_count=120,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_chunk() -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id="doc-1::0",
        document_id="doc-1",
        text="The pyramids of Giza were built during the Old Kingdom.",
        title="The Old Kingdom",
        author="J. Historian",
        era="Ancient Egypt",
        source_type="book",
        distance=0.1,
    )
