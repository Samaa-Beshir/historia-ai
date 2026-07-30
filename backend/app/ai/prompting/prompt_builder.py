"""Builds the system instruction and user prompt sent to the LLM from
retrieved chunks. Kept separate from the LLM provider so prompt wording
can change without touching provider code.
"""
from app.ai.retrieval.models import RetrievedChunk

_SYSTEM_PROMPT = """You are Historia AI, a research assistant that answers questions about \
Egyptian history strictly using the CONTEXT excerpts provided with each question.

Rules:
- Answer only using facts supported by the CONTEXT. Do not use outside knowledge.
- If the CONTEXT does not contain the answer, say so plainly instead of guessing.
- Cite sources inline using the bracketed numbers shown next to each excerpt, e.g. [1].
- Be concise and precise, in a tone suited to historical research.
"""


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def build_user_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        context_block = "(no relevant context was found)"
    else:
        context_block = "\n\n".join(
            f"[{i}] ({chunk.era} — {chunk.title}, {chunk.author})\n{chunk.text}"
            for i, chunk in enumerate(chunks, start=1)
        )

    return f"CONTEXT:\n{context_block}\n\nQUESTION:\n{question}"
