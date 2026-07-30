"""Selects the configured LLM provider.

Adding a new provider means writing a class that implements LLMProvider
and registering it here — nothing else in the AI/service layers changes.
"""
from app.ai.llm.base import LLMProvider
from app.ai.llm.gemini_provider import GeminiProvider
from app.config.settings import Settings
from app.core.exceptions import ConfigurationError


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "gemini":
        if settings.gemini_api_key is None:
            raise ConfigurationError("LLM_PROVIDER is 'gemini' but GEMINI_API_KEY is not set.")
        return GeminiProvider(
            api_key=settings.gemini_api_key.get_secret_value(),
            model_name=settings.gemini_model,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_output_tokens,
        )

    raise ConfigurationError(
        f"LLM_PROVIDER={settings.llm_provider!r} has no implementation registered. "
        "Add an adapter implementing LLMProvider and register it in app/ai/llm/factory.py."
    )
