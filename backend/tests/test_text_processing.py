from app.scripts.text_processing import chunk_text, clean_text


def test_clean_text_strips_page_numbers_and_blank_lines():
    raw = "Chapter One\n\n12\nThe Nile flows north.\n\n"
    cleaned = clean_text(raw)
    assert "12" not in cleaned.split("\n")
    assert "The Nile flows north." in cleaned


def test_clean_text_collapses_inline_whitespace():
    cleaned = clean_text("The   Nile    flows   north.")
    assert cleaned == "The Nile flows north."


def test_chunk_text_respects_size_and_overlap():
    text = "a" * 25
    chunks = chunk_text(text, chunk_size_chars=10, overlap_chars=2)

    assert all(len(c) <= 10 for c in chunks)
    assert len(chunks) > 1


def test_chunk_text_empty_input_returns_no_chunks():
    assert chunk_text("", chunk_size_chars=10, overlap_chars=2) == []
