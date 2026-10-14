from services.chunker import TextChunk
from services.vector_store import VectorStore

class FakeEmbedder:
    def embed_documents(self, texts):
        return [[float(len(t)), 1.0, 0.0] for t in texts]
    def embed_query(self, text):
        return [float(len(text)), 1.0, 0.0]

def chunk(did, filename, text, page=1):
    return TextChunk(text, {"document_id": did, "filename": filename, "page": page, "chunk_index": 0})

def test_index_search_duplicate_delete_and_clear(tmp_path):
    store = VectorStore(tmp_path / "db", "test", FakeEmbedder())
    assert store.list_documents() == []
    assert store.add_document("a", [chunk("a", "a.pdf", "alpha science")])
    assert not store.add_document("a", [chunk("a", "a.pdf", "alpha science")])
    assert store.add_document("b", [chunk("b", "b.pdf", "beta biology", 2)])
    assert store.list_documents() == [
        {"document_id": "a", "filename": "a.pdf", "chunks": 1},
        {"document_id": "b", "filename": "b.pdf", "chunks": 1},
    ]
    assert store.search("alpha science")[0]["filename"] == "a.pdf"
    store.delete_document("a")
    assert [d["document_id"] for d in store.list_documents()] == ["b"]
    store.clear()
    assert store.list_documents() == []
