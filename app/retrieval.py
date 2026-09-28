from embeddings import create_embedding
from vector_store import collection
from reranker import rerank_documents
from query_rewriter import rewrite_query


def retrieve_documents(query: str, k: int = 5):

    # 1. Rewrite the user's query for better retrieval
    search_query = rewrite_query(query)

    # 2. Create embedding from the rewritten query
    query_embedding = create_embedding(search_query)

    # 3. Retrieve more candidates
    candidate_k = 10

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=candidate_k
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    # 4. Rerank the candidates
    ranked_documents = rerank_documents(
        search_query,
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
        "scores": final_scores,
        "search_query": search_query
    }