"""Restore the shipped vector index and warm the embedding model cache.

Usage:
    python -m app.scripts.prepare_index

Intended to run at deploy *build* time, not at request time. The vector index
is too large to commit uncompressed, so it ships as data/chroma_index.tar.gz
and is expanded here. The ONNX embedding model is downloaded on first use from
S3 (~167MB); doing that during the build keeps it off the cold-start path,
which matters on hosts with an ephemeral filesystem.

Both steps are idempotent — re-running is a no-op once the index exists and the
model is cached.
"""
import sys
import tarfile
from pathlib import Path

from app.ai.embeddings.factory import build_embedding_provider
from app.config.settings import Settings
from app.config.settings import get_settings
from app.core.logging import configure_logging, get_logger

logger = get_logger(__name__)

_ARCHIVE_NAME = "chroma_index.tar.gz"


def restore_index(archive_path: Path, persist_dir: Path) -> bool:
    """Expand the index archive unless a populated index is already present."""
    if any(persist_dir.glob("*.sqlite3")):
        logger.info("Index already present at %s; skipping restore", persist_dir)
        return False

    if not archive_path.exists():
        logger.error("Index archive not found at %s", archive_path)
        sys.exit(1)

    # The archive holds a top-level `chroma/` directory, so extract into the
    # parent and let it land on persist_dir itself.
    logger.info("Restoring index from %s", archive_path)
    with tarfile.open(archive_path, "r:gz") as tar:
        tar.extractall(persist_dir.parent)

    if not any(persist_dir.glob("*.sqlite3")):
        logger.error("Archive extracted but no sqlite file found under %s", persist_dir)
        sys.exit(1)

    logger.info("Index restored to %s", persist_dir)
    return True


def warm_embedding_model(settings: Settings) -> None:
    """Trigger the one-time ONNX model download so it happens during build."""
    logger.info("Warming embedding model cache")
    build_embedding_provider(settings).embed_query("warmup")
    logger.info("Embedding model ready")


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    persist_dir = settings.chroma_persist_dir
    persist_dir.mkdir(parents=True, exist_ok=True)

    restore_index(persist_dir.parent / _ARCHIVE_NAME, persist_dir)
    warm_embedding_model(settings)

    logger.info("Index preparation complete")


if __name__ == "__main__":
    main()
