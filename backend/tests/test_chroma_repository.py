from app.data.chroma_repository import ChromaRepository


def _fake_embedding(seed: float) -> list[float]:
    return [seed, 1 - seed, 0.0]


def test_add_and_query_returns_nearest(tmp_path):
    repo = ChromaRepository(tmp_path / "chroma", "test_collection")

    repo.add(
        ids=["a", "b"],
        embeddings=[_fake_embedding(0.9), _fake_embedding(0.1)],
        documents=["chunk about era A", "chunk about era B"],
        metadatas=[{"era": "Ancient Egypt"}, {"era": "Islamic Egypt"}],
    )

    result = repo.query(_fake_embedding(0.95), top_k=1)

    assert result["ids"][0] == ["a"]
    assert repo.count() == 2


def test_query_with_where_filter(tmp_path):
    repo = ChromaRepository(tmp_path / "chroma", "test_collection")
    repo.add(
        ids=["a", "b"],
        embeddings=[_fake_embedding(0.9), _fake_embedding(0.1)],
        documents=["chunk A", "chunk B"],
        metadatas=[{"era": "Ancient Egypt"}, {"era": "Islamic Egypt"}],
    )

    result = repo.query(_fake_embedding(0.5), top_k=5, where={"era": "Islamic Egypt"})

    assert result["ids"][0] == ["b"]


def test_reset_clears_collection(tmp_path):
    repo = ChromaRepository(tmp_path / "chroma", "test_collection")
    repo.add(ids=["a"], embeddings=[_fake_embedding(0.5)], documents=["x"], metadatas=[{"era": "X"}])

    repo.reset()

    assert repo.count() == 0


def test_existing_ids_returns_only_stored_ids(tmp_path):
    repo = ChromaRepository(tmp_path / "chroma", "test_collection")
    repo.add(ids=["a"], embeddings=[_fake_embedding(0.5)], documents=["x"], metadatas=[{"era": "X"}])

    assert repo.existing_ids(["a", "missing"]) == {"a"}
    assert repo.existing_ids([]) == set()
