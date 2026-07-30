"""Read-only service over the document catalog (metadata.csv)."""
from app.data.metadata_repository import MetadataRepository
from app.data.models import DocumentMetadata


class DocumentService:
    def __init__(self, metadata_repository: MetadataRepository):
        self._metadata = metadata_repository

    def list_eras(self) -> list[str]:
        return self._metadata.list_eras()

    def list_documents(self, era: str | None = None) -> list[DocumentMetadata]:
        return self._metadata.filter(era=era)
