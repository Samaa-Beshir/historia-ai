"""Route-level tests using FastAPI dependency_overrides.

The real app lifespan loads a Sentence-Transformers model and configures
an LLM provider — too heavy for unit tests. These tests build the app via
create_app() without entering it as a context manager (so lifespan never
runs) and inject fakes for every dependency a route needs.
"""
from fastapi.testclient import TestClient

from app.core.dependencies import get_chat_service, get_document_service, get_settings_dep
from app.data.models import DocumentMetadata
from app.main import create_app
from app.services.chat_service import ChatResult


class FakeChatService:
    def ask(self, question, era=None, top_k=None):
        return ChatResult(answer="42", sources=[])


class FakeDocumentService:
    def list_eras(self):
        return ["Ancient Egypt", "Islamic Egypt"]

    def list_documents(self, era=None):
        doc = DocumentMetadata(
            document_id="doc-1",
            filename="a.pdf",
            relative_path="books/Ancient_Egypt/a.pdf",
            era="Ancient Egypt",
            source_type="book",
            title="Title",
            author="Author",
            page_count=10,
            created_at="2024-01-01T00:00:00Z",
        )
        return [doc] if era in (None, "Ancient Egypt") else []


def make_client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_chat_service] = lambda: FakeChatService()
    app.dependency_overrides[get_document_service] = lambda: FakeDocumentService()
    app.dependency_overrides[get_settings_dep] = lambda: app.state.settings if hasattr(app.state, "settings") else __import__("app.config.settings", fromlist=["get_settings"]).get_settings()
    return TestClient(app)


def test_health_endpoint():
    client = make_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_endpoint_returns_answer():
    client = make_client()
    response = client.post("/api/chat", json={"question": "Who built the pyramids?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "42"


def test_chat_endpoint_rejects_empty_question():
    client = make_client()
    response = client.post("/api/chat", json={"question": ""})
    assert response.status_code == 422


def test_eras_endpoint():
    client = make_client()
    response = client.get("/api/eras")
    assert response.status_code == 200
    assert "Ancient Egypt" in response.json()["eras"]


def test_documents_endpoint_filters_by_era():
    client = make_client()
    response = client.get("/api/documents", params={"era": "Islamic Egypt"})
    assert response.status_code == 200
    assert response.json()["documents"] == []
