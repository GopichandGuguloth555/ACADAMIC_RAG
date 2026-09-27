from ingestion import load_pdf
from chunking import split_documents
from embeddings import create_embedding
from vector_store import add_documents


pdf_path = "../data/documents/testData.pdf"

# 1. Load PDF
documents = load_pdf(pdf_path)

# 2. Split into chunks
chunks = split_documents(documents)

# 3. Create embeddings
texts = [chunk.page_content for chunk in chunks]

embeddings = create_embedding(texts)

# 4. Store in ChromaDB
add_documents(chunks, embeddings)