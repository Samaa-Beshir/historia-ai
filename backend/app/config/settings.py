"""Centralized, environment-driven configuration.

Every tunable value in the application flows through this module. Nothing
downstream should hardcode a model name, path, or secret.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "Historia AI"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # --- Security / cross-cutting ---
    api_key: SecretStr | None = Field(default=None, description="If set, required via X-API-Key header.")
    rate_limit_per_minute: int = Field(default=60)

    # --- Data locations ---
    raw_books_dir: Path = Field(default=PROJECT_ROOT / "data" / "row")
    processed_dir: Path = Field(default=PROJECT_ROOT / "data" / "processed")
    metadata_csv_path: Path = Field(default=PROJECT_ROOT / "data" / "metadata.csv")
    chroma_persist_dir: Path = Field(default=PROJECT_ROOT / "data" / "chroma")
    chroma_collection_name: str = Field(default="historia_documents")

    # --- Chunking ---
    chunk_size_chars: int = Field(default=1200)
    chunk_overlap_chars: int = Field(default=200)

    # --- Embeddings ---
    embedding_provider: str = Field(default="onnx_minilm")
    embedding_model_name: str = Field(default="all-MiniLM-L6-v2")

    # --- Retrieval ---
    retrieval_top_k: int = Field(default=5)

    # --- LLM ---
    llm_provider: str = Field(default="gemini")
    gemini_api_key: SecretStr | None = Field(default=None)
    gemini_model: str = Field(default="gemini-2.0-flash")
    openai_api_key: SecretStr | None = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    anthropic_api_key: SecretStr | None = Field(default=None)
    anthropic_model: str = Field(default="claude-sonnet-5")
    llm_temperature: float = Field(default=0.2)
    llm_max_output_tokens: int = Field(default=1024)

    @field_validator("api_key", "gemini_api_key", "openai_api_key", "anthropic_api_key", mode="before")
    @classmethod
    def _blank_secret_is_unset(cls, value: str | None) -> str | None:
        """An empty string in .env (e.g. `API_KEY=`) means "not set", not a literal empty secret."""
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a process-wide cached Settings instance."""
    return Settings()
