"""FastAPI dependency providers.

Expensive singletons (embedding model, Chroma client, LLM provider) are
built once in main.py's lifespan and stored on `app.state`; these
dependencies just fetch them per-request, keeping routes free of
construction logic.
"""
from fastapi import Request

from app.config.settings import Settings
from app.core.exceptions import ConfigurationError
from app.data.metadata_repository import MetadataRepository
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings


def get_metadata_repository(request: Request) -> MetadataRepository:
    return request.app.state.metadata_repository


def get_document_service(request: Request) -> DocumentService:
    return DocumentService(get_metadata_repository(request))


def get_chat_service(request: Request) -> ChatService:
    chat_service = getattr(request.app.state, "chat_service", None)
    if chat_service is None:
        raise ConfigurationError(
            "Chat service is unavailable: the LLM provider failed to initialize "
            "(check LLM_PROVIDER and the matching API key in your environment)."
        )
    return chat_service
