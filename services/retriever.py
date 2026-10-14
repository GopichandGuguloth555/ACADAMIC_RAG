"""Evidence retrieval and citation formatting."""
from typing import Any
from config import MIN_RELEVANCE, RETRIEVAL_K

def retrieve(store: Any, question: str, k: int = RETRIEVAL_K, threshold: float = MIN_RELEVANCE) -> list[dict[str, Any]]:
    if not question.strip():
        raise ValueError("Enter a question to search the documents.")
    return [hit for hit in store.search(question, k) if hit["relevance"] >= threshold]

def citation_label(source: dict[str, Any]) -> str:
    return f"{source['filename']}, p. {source['page']}"
