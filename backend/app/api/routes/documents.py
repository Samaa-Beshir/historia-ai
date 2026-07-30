from fastapi import APIRouter, Depends

from app.api.schemas.documents import DocumentListResponse, DocumentSchema, EraListResponse
from app.core.dependencies import get_document_service
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api", tags=["documents"])


@router.get("/eras", response_model=EraListResponse)
def get_eras(service: DocumentService = Depends(get_document_service)) -> EraListResponse:
    return EraListResponse(eras=service.list_eras())


@router.get("/documents", response_model=DocumentListResponse)
def get_documents(
    era: str | None = None,
    service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    documents = service.list_documents(era=era)
    return DocumentListResponse(
        documents=[
            DocumentSchema(
                document_id=d.document_id,
                title=d.title,
                author=d.author,
                era=d.era,
                source_type=d.source_type,
                page_count=d.page_count,
            )
            for d in documents
        ]
    )
