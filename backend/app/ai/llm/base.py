"""LLM provider abstraction — the AI layer talks to this, never to a
provider SDK directly, so the model behind /api/chat can be swapped via
configuration alone.
"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, *, system_prompt: str, user_message: str) -> str:
        """Generate a response given a system instruction and user content."""
