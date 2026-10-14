import pytest
from types import SimpleNamespace
from services.rag_service import RAGService, INSUFFICIENT_ANSWER
from services.llm_service import GeminiService
from services.retriever import citation_label

class EmptyStore:
    def search(self, query, k):
        return []

class EvidenceStore:
    def search(self, query, k):
        return [{"text": "The trial included 120 participants.", "filename": "trial.pdf", "page": 4,
                 "document_id": "abc", "chunk_index": 0, "distance": 0.1, "relevance": 0.9}]

class FakeLLM:
    def __init__(self): self.seen = None
    def answer(self, question, sources):
        self.seen = (question, sources)
        return "The trial included 120 participants [trial.pdf, p. 4]."

def test_no_evidence_is_honest_and_never_calls_llm():
    llm = FakeLLM()
    result = RAGService(EmptyStore(), llm).ask("How many participants?")
    assert result == {"answer": INSUFFICIENT_ANSWER, "sources": []}
    assert llm.seen is None

def test_answer_passes_real_citation_metadata():
    llm = FakeLLM()
    result = RAGService(EvidenceStore(), llm).ask("How many participants?")
    assert result["sources"][0]["filename"] == "trial.pdf"
    assert result["sources"][0]["page"] == 4
    assert "trial.pdf, p. 4" in result["answer"]
    assert llm.seen[1] == result["sources"]

def test_missing_api_key_is_clear():
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        GeminiService(api_key="").answer("question", [{"filename":"x.pdf", "page":1, "text":"x"}])

def test_citation_label_uses_filename_and_one_based_page():
    assert citation_label({"filename": "paper.pdf", "page": 7}) == "paper.pdf, p. 7"

def test_gemini_request_contains_only_supplied_evidence(monkeypatch):
    import google.genai
    captured = {}

    class FakeModels:
        def generate_content(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(text="The trial enrolled 120 people [trial.pdf, p. 4].")

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.models = FakeModels()

    monkeypatch.setattr(google.genai, "Client", FakeClient)
    answer = GeminiService(api_key="test-key").answer("How many?", [{
        "filename": "trial.pdf", "page": 4, "text": "The trial enrolled 120 people."
    }])
    assert "120 people" in answer
    assert "[trial.pdf, p. 4]" in captured["contents"]
    assert "Never invent citations" in captured["config"].system_instruction

def test_gemini_reports_temporary_server_errors(monkeypatch):
    import google.genai

    class TemporaryFailure(Exception):
        code = 503

    class FailedClient:
        def __init__(self, api_key):
            self.models = SimpleNamespace(generate_content=lambda **kwargs: (_ for _ in ()).throw(TemporaryFailure()))

    monkeypatch.setattr(google.genai, "Client", FailedClient)
    with pytest.raises(RuntimeError, match=r"temporarily unavailable \(HTTP 503\)"):
        GeminiService(api_key="test-key").answer("question", [{"filename": "x.pdf", "page": 1, "text": "evidence"}])

def test_blank_question_and_retriever_errors():
    with pytest.raises(ValueError, match="question"):
        RAGService(EmptyStore()).ask(" ")
