from app.ai.prompting.prompt_builder import build_system_prompt, build_user_prompt


def test_system_prompt_instructs_grounding():
    prompt = build_system_prompt()
    assert "CONTEXT" in prompt
    assert "cite" in prompt.lower()


def test_user_prompt_includes_numbered_citations(sample_chunk):
    prompt = build_user_prompt("Who built the pyramids?", [sample_chunk])

    assert "[1]" in prompt
    assert sample_chunk.text in prompt
    assert "Who built the pyramids?" in prompt


def test_user_prompt_handles_no_chunks():
    prompt = build_user_prompt("Unanswerable question", [])
    assert "no relevant context" in prompt.lower()
