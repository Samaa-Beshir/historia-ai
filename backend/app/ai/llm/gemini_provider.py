"""Google Gemini implementation of the LLM provider interface."""
import google.generativeai as genai

from app.ai.llm.base import LLMProvider
from app.core.exceptions import LLMProviderError
from app.core.logging import get_logger

logger = get_logger(__name__)


class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str, temperature: float, max_output_tokens: int):
        genai.configure(api_key=api_key)
        self._model_name = model_name
        self._generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    def generate(self, *, system_prompt: str, user_message: str) -> str:
        try:
            model = genai.GenerativeModel(
                model_name=self._model_name,
                system_instruction=system_prompt,
            )
            response = model.generate_content(user_message, generation_config=self._generation_config)
            return response.text
        except Exception as exc:
            # The SDK's exception text can be very long (multi-line quota/policy
            # dumps); log it in full server-side but keep the client-facing
            # message short and free of provider implementation details.
            logger.error("Gemini generation failed: %s", exc)
            raise LLMProviderError("The AI provider is temporarily unavailable. Please try again shortly.") from exc
