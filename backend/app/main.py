"""Application entrypoint: wires configuration, singletons, middleware,
exception handling, and routers together. No business logic lives here.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai.embeddings.onnx_minilm_provider import OnnxMiniLMEmbeddingProvider
from app.ai.llm.factory import build_llm_provider
from app.ai.retrieval.retriever import Retriever
from app.api.routes import chat, documents, health
from app.config.settings import get_settings
from app.core.exceptions import ConfigurationError, HistoriaError
from app.core.logging import configure_logging, get_logger
from app.core.middleware import ApiKeyMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from app.data.chroma_repository import ChromaRepository
from app.data.metadata_repository import MetadataRepository
from app.services.chat_service import ChatService

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)

    app.state.settings = settings
    app.state.metadata_repository = MetadataRepository(settings.metadata_csv_path)

    logger.info("Loading embedding model %r ...", settings.embedding_model_name)
    embedding_provider = OnnxMiniLMEmbeddingProvider(settings.embedding_model_name)
    chroma_repository = ChromaRepository(settings.chroma_persist_dir, settings.chroma_collection_name)
    retriever = Retriever(chroma_repository, embedding_provider)

    try:
        llm_provider = build_llm_provider(settings)
        app.state.chat_service = ChatService(retriever, llm_provider, settings.retrieval_top_k)
        logger.info("LLM provider %r ready.", settings.llm_provider)
    except ConfigurationError as exc:
        logger.warning("Chat service disabled at startup: %s", exc)
        app.state.chat_service = None

    logger.info("Historia AI backend ready (%d documents indexed).", chroma_repository.count())
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True,
                        allow_methods=["*"], allow_headers=["*"])
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)
    app.add_middleware(ApiKeyMiddleware, settings=settings)
    app.add_middleware(RequestLoggingMiddleware)

    @app.exception_handler(HistoriaError)
    async def historia_error_handler(request: Request, exc: HistoriaError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(health.router)
    app.include_router(chat.router)
    app.include_router(documents.router)

    return app


app = create_app()
