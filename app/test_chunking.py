from ingestion import load_pdf
from chunking import split_documents


pdf_path = "../data/documents/testData.pdf"

documents = load_pdf(pdf_path)

chunks = split_documents(documents)

print("Total pages:", len(documents))
print("Total chunks:", len(chunks))

print("\n--- First chunk ---")
print(chunks[0].page_content)

print("\n--- First chunk metadata ---")
print(chunks[0].metadata)