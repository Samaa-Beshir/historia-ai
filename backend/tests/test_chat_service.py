from app.ai.llm.base import LLMProvider
from app.services.chat_service import ChatService


class FakeRetriever:
    def __init__(self, chunks):
        self._chunks = chunks
        self.last_call = None

    def retrieve(self, query, top_k, era=None):
        self.last_call = (query, top_k, era)
        return self._chunks


class FakeLLMProvider(LLMProvider):
    def __init__(self):
        self.last_call = None

    def generate(self, *, system_prompt: str, user_message: str) -> str:
        self.last_call = (system_prompt, user_message)
        return "The pyramids were built in the Old Kingdom [1]."


def test_ask_retrieves_before_generating(sample_chunk):
    retriever = FakeRetriever([sample_chunk])
    llm = FakeLLMProvider()
    service = ChatService(retriever, llm, default_top_k=5)

    result = service.ask("Who built the pyramids?", era="Ancient Egypt")

    assert retriever.last_call == ("Who built the pyramids?", 5, "Ancient Egypt")
    assert llm.last_call is not None
    assert result.answer.startswith("The pyramids")
    assert result.sources == [sample_chunk]


def test_ask_respects_explicit_top_k(sample_chunk):
    retriever = FakeRetriever([sample_chunk])
    service = ChatService(retriever, FakeLLMProvider(), default_top_k=5)

    service.ask("question", top_k=2)

    assert retriever.last_call[1] == 2
