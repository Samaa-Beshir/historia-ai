from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    era: str | None = Field(default=None, description="Optional era filter, e.g. 'Ancient Egypt'.")
    top_k: int | None = Field(default=None, ge=1, le=20)


class SourceSchema(BaseModel):
    document_id: str
    title: str
    author: str
    era: str
    source_type: str
    snippet: str
    relevance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceSchema]
