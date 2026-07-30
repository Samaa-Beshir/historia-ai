from fastapi import APIRouter, Depends

from app.api.schemas.chat import ChatRequest, ChatResponse, SourceSchema
from app.core.dependencies import get_chat_service
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def post_chat(payload: ChatRequest, chat_service: ChatService = Depends(get_chat_service)) -> ChatResponse:
    result = chat_service.ask(question=payload.question, era=payload.era, top_k=payload.top_k)

    sources = [
        SourceSchema(
            document_id=source.document_id,
            title=source.title,
            author=source.author,
            era=source.era,
            source_type=source.source_type,
            snippet=source.text[:280],
            relevance=round(max(0.0, 1 - source.distance), 4),
        )
        for source in result.sources
    ]
    return ChatResponse(answer=result.answer, sources=sources)
