from app.ai.embeddings.base import EmbeddingProvider
from app.ai.retrieval.retriever import Retriever
from app.data.chroma_repository import ChromaRepository


class FakeEmbeddingProvider(EmbeddingProvider):
    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


def test_retrieve_returns_typed_chunks(tmp_path):
    chroma = ChromaRepository(tmp_path / "chroma", "test_collection")
    chroma.add(
        ids=["doc-1::0"],
        embeddings=[[1.0, 0.0, 0.0]],
        documents=["The pyramids were built in the Old Kingdom."],
        metadatas=[
            {
                "document_id": "doc-1",
                "title": "The Old Kingdom",
                "author": "J. Historian",
                "era": "Ancient Egypt",
                "source_type": "book",
            }
        ],
    )
    retriever = Retriever(chroma, FakeEmbeddingProvider())

    chunks = retriever.retrieve("Who built the pyramids?", top_k=3)

    assert len(chunks) == 1
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].era == "Ancient Egypt"


def test_retrieve_applies_era_filter(tmp_path):
    chroma = ChromaRepository(tmp_path / "chroma", "test_collection")
    chroma.add(
        ids=["doc-1::0", "doc-2::0"],
        embeddings=[[1.0, 0.0, 0.0], [1.0, 0.0, 0.0]],
        documents=["ancient text", "islamic text"],
        metadatas=[
            {"document_id": "doc-1", "title": "T1", "author": "A1", "era": "Ancient Egypt", "source_type": "book"},
            {"document_id": "doc-2", "title": "T2", "author": "A2", "era": "Islamic Egypt", "source_type": "book"},
        ],
    )
    retriever = Retriever(chroma, FakeEmbeddingProvider())

    chunks = retriever.retrieve("query", top_k=5, era="Islamic Egypt")

    assert len(chunks) == 1
    assert chunks[0].era == "Islamic Egypt"
