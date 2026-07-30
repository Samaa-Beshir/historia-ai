"""Text extraction, cleaning, and chunking used by the offline data
pipeline (build_chunks.py). Chunks contain cleaned text only — no
metadata is embedded into the text itself (DATA_PIPELINE.md).
"""
import re

from pypdf import PdfReader


def extract_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)


def clean_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse runs of whitespace within a line.
    text = re.sub(r"[ \t]+", " ", text)
    # Drop lines that are just page numbers or empty after stripping.
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line and not re.fullmatch(r"\d{1,4}", line)]
    return "\n".join(lines)


def chunk_text(text: str, chunk_size_chars: int, overlap_chars: int) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    length = len(text)
    step = max(chunk_size_chars - overlap_chars, 1)

    while start < length:
        end = min(start + chunk_size_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == length:
            break
        start += step

    return chunks
