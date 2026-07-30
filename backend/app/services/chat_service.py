"""Orchestrates a single chat turn: retrieve -> build prompt -> generate.

This is the only place that sequences the RAG pipeline; the API layer
just calls `ask` and serializes the result.
"""
from pydantic import BaseModel

from app.ai.llm.base import LLMProvider
from app.ai.prompting.prompt_builder import build_system_prompt, build_user_prompt
from app.ai.retrieval.models import RetrievedChunk
from app.ai.retrieval.retriever import Retriever
from app.core.logging import get_logger

logger = get_logger(__name__)


class ChatResult(BaseModel):
    answer: str
    sources: list[RetrievedChunk]


class ChatService:
    def __init__(self, retriever: Retriever, llm_provider: LLMProvider, default_top_k: int):
        self._retriever = retriever
        self._llm = llm_provider
        self._default_top_k = default_top_k

    def ask(self, question: str, era: str | None = None, top_k: int | None = None) -> ChatResult:
        chunks: list[RetrievedChunk] = self._retriever.retrieve(
            query=question,
            top_k=top_k or self._default_top_k,
            era=era,
        )

        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(question, chunks)
        answer = self._llm.generate(system_prompt=system_prompt, user_message=user_prompt)

        logger.info("Answered question (era=%s, %d sources)", era, len(chunks))
        return ChatResult(answer=answer, sources=chunks)
