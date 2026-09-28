from embeddings import create_embedding
from vector_store import collection
from reranker import rerank_documents


def retrieve_documents(query: str, k: int = 5):

    candidate_k = 10

    query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    ranked_documents = rerank_documents(
        query,
        documents,
        metadatas,
        top_k=k
    )

    final_documents = []
    final_metadatas = []
    final_scores = []

    for document, metadata, score in ranked_documents:
        final_documents.append(document)
        final_metadatas.append(metadata)
        final_scores.append(float(score))

    return {
        "documents": final_documents,
        "metadatas": final_metadatas,
        "scores": final_scores
    }