from services.chunker import chunk_pages

def test_chunks_overlap_and_preserve_metadata():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunk_pages([{"page": 3, "text": text}], "doc", "paper.pdf", chunk_size=10, overlap=2)
    assert [c.text for c in chunks] == [text[0:10], text[8:18], text[16:26], text[24:26]]
    assert all(c.metadata["page"] == 3 for c in chunks)
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(4))
    assert all(c.metadata["document_id"] == "doc" for c in chunks)
