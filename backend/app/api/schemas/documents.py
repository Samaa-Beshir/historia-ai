from pydantic import BaseModel


class DocumentSchema(BaseModel):
    document_id: str
    title: str
    author: str
    era: str
    source_type: str
    page_count: int


class DocumentListResponse(BaseModel):
    documents: list[DocumentSchema]


class EraListResponse(BaseModel):
    eras: list[str]
