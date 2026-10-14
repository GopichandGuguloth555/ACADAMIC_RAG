"""Persistent Chroma document store."""
from pathlib import Path
from typing import Any
import chromadb
from chromadb.config import Settings
from config import CHROMA_DIR, COLLECTION_NAME, ensure_data_dirs
from services.embeddings import SentenceTransformerEmbedder, get_embedder

class VectorStore:
    def __init__(self, path: str | Path = CHROMA_DIR, collection_name: str = COLLECTION_NAME,
                 embedder: SentenceTransformerEmbedder | None = None):
        self.path = Path(path).resolve()
        self.collection_name = collection_name
        self.path.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder or get_embedder()
        try:
            self.client = chromadb.PersistentClient(path=str(self.path), settings=Settings(anonymized_telemetry=False))
            self.collection = self.client.get_or_create_collection(collection_name, metadata={"hnsw:space": "cosine"})
        except Exception as exc:
            raise RuntimeError("Could not initialize the local document index.") from exc

    def add_document(self, document_id: str, chunks: list[Any]) -> bool:
        if self.document_exists(document_id):
            return False
        if not chunks:
            raise ValueError("There is no extractable text to index.")
        texts = [c.text for c in chunks]
        embeddings = self.embedder.embed_documents(texts)
        self.collection.add(ids=[f"{document_id}:{i}" for i in range(len(chunks))], documents=texts,
                            metadatas=[c.metadata for c in chunks], embeddings=embeddings)
        return True

    def document_exists(self, document_id: str) -> bool:
        return bool(self.collection.get(where={"document_id": document_id}, include=[])["ids"])

    def list_documents(self) -> list[dict[str, Any]]:
        rows = self.collection.get(include=["metadatas"])
        docs: dict[str, dict[str, Any]] = {}
        for meta in rows.get("metadatas") or []:
            did = meta["document_id"]
            item = docs.setdefault(did, {"document_id": did, "filename": meta["filename"], "chunks": 0})
            item["chunks"] += 1
        return sorted(docs.values(), key=lambda x: x["filename"].lower())

    def search(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        if self.collection.count() == 0:
            return []
        result = self.collection.query(query_embeddings=[self.embedder.embed_query(query)], n_results=min(k, self.collection.count()),
                                       include=["documents", "metadatas", "distances"])
        found = []
        for doc, meta, distance in zip(result["documents"][0], result["metadatas"][0], result["distances"][0]):
            found.append({"text": doc, **meta, "distance": float(distance), "relevance": 1 - float(distance)})
        return found

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})

    def clear(self) -> None:
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(self.collection_name, metadata={"hnsw:space": "cosine"})
