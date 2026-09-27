from embeddings import create_embedding
from vector_store import collection


def retrieve_documents(query: str, k: int = 5):

    # Convert the user's question into an embedding
    query_embedding = create_embedding(query)

    # Search ChromaDB for similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    return results