from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    title: str
    author: str
    era: str
    source_type: str
    distance: float
