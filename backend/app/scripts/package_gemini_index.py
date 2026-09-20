"""Package the completed Gemini Chroma index for deployment."""
import tarfile
from pathlib import Path

from app.config.settings import PROJECT_ROOT

SOURCE_DIR = PROJECT_ROOT / "data" / "chroma_experiments" / "gemini_embedding_001"
OUTPUT_PATH = PROJECT_ROOT / "data" / "chroma_gemini_index.tar.gz"
TEMP_PATH = PROJECT_ROOT / "data" / "chroma_gemini_index.tar.gz.tmp"


def main() -> None:
    sqlite_path = SOURCE_DIR / "chroma.sqlite3"
    if not sqlite_path.exists():
        raise SystemExit(f"Completed Gemini index was not found at {SOURCE_DIR}")

    if TEMP_PATH.exists():
        TEMP_PATH.unlink()

    print(f"Packaging index from: {SOURCE_DIR}")
    with tarfile.open(TEMP_PATH, "w:gz") as archive:
        archive.add(SOURCE_DIR, arcname="chroma")

    with tarfile.open(TEMP_PATH, "r:gz") as archive:
        names = set(archive.getnames())
        if "chroma/chroma.sqlite3" not in names:
            raise SystemExit("Archive verification failed: chroma/chroma.sqlite3 is missing")

    TEMP_PATH.replace(OUTPUT_PATH)
    size_mb = OUTPUT_PATH.stat().st_size / (1024 * 1024)
    print("Archive verification passed.")
    print(f"Created: {OUTPUT_PATH}")
    print(f"Archive size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
