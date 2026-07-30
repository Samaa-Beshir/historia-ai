from app.core.exceptions import NotFoundError
from app.data.metadata_repository import MetadataRepository


def test_save_and_load_round_trip(tmp_path, sample_document):
    repo = MetadataRepository(tmp_path / "metadata.csv")
    repo.save_all([sample_document])

    loaded = repo.load_all()

    assert len(loaded) == 1
    assert loaded[0].document_id == sample_document.document_id
    assert loaded[0].era == "Ancient Egypt"


def test_get_missing_document_raises(tmp_path):
    repo = MetadataRepository(tmp_path / "metadata.csv")
    repo.save_all([])

    try:
        repo.get("missing")
        assert False, "expected NotFoundError"
    except NotFoundError:
        pass


def test_filter_by_era(tmp_path, sample_document):
    other = sample_document.model_copy(update={"document_id": "doc-2", "era": "Islamic Egypt"})
    repo = MetadataRepository(tmp_path / "metadata.csv")
    repo.save_all([sample_document, other])

    ancient_only = repo.filter(era="Ancient Egypt")

    assert [d.document_id for d in ancient_only] == ["doc-1"]
    assert set(repo.list_eras()) == {"Ancient Egypt", "Islamic Egypt"}
