"""Question answering orchestration."""
from typing import Any
from services.retriever import retrieve
from services.llm_service import GeminiService

INSUFFICIENT_ANSWER = "The uploaded documents do not provide enough evidence to answer this question."

class RAGService:
    def __init__(self, store: Any, llm: GeminiService | Any | None = None):
        self.store = store
        self.llm = llm or GeminiService()

    def ask(self, question: str) -> dict[str, Any]:
        if not question or not question.strip():
            raise ValueError("Enter a question first.")
        sources = retrieve(self.store, question)
        if not sources:
            return {"answer": INSUFFICIENT_ANSWER, "sources": []}
        return {"answer": self.llm.answer(question.strip(), sources), "sources": sources}
