import chromadb

client = chromadb.PersistentClient(
    path="../data/vectorstore"
)

collection = client.get_or_create_collection(
    name="academic_documents"
)


def add_documents(chunks, embeddings):

    ids = [
        f"chunk_{chunk.metadata['chunk_id']}"
        for chunk in chunks
    ]

    documents = [
        chunk.page_content
        for chunk in chunks
    ]

    metadatas = [
        chunk.metadata
        for chunk in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Stored {len(chunks)} chunks in ChromaDB")