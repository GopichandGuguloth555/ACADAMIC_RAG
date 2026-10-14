"""Text chunking with page-local source metadata."""
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class TextChunk:
    text: str
    metadata: dict[str, Any]

def chunk_pages(pages: list[dict[str, Any]], document_id: str, filename: str,
                chunk_size: int = 1000, overlap: int = 160) -> list[TextChunk]:
    if chunk_size < 1 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap smaller than chunk_size")
    chunks: list[TextChunk] = []
    step = chunk_size - overlap
    for page in pages:
        text = " ".join(str(page.get("text", "")).split())
        start = 0
        while start < len(text):
            part = text[start:start + chunk_size].strip()
            if part:
                chunks.append(TextChunk(part, {
                    "document_id": document_id, "filename": filename,
                    "page": int(page["page"]), "chunk_index": len(chunks),
                }))
            start += step
    return chunks
