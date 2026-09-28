from retrieval import retrieve_documents
from llm import generate_answer
from context_builder import build_context


def answer_question(query: str, k: int = 5):

    # Retrieve and rerank documents
    results = retrieve_documents(query, k=k)

    documents = results["documents"]
    metadatas = results["metadatas"]

    # Build optimized context
    context = build_context(
        documents,
        metadatas
    )

    prompt = f"""
You are an academic knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not invent information.
- If the answer is not present in the context, say:
  "I don't have enough information in the provided documents."
- Give a clear and concise answer.
- Mention the relevant source numbers when possible.

Context:
{context}

Question:
{query}

Answer:
"""

    answer = generate_answer(prompt)

    sources = []

    for metadata in metadatas:
        sources.append({
            "document": metadata.get("document_name"),
            "page": metadata.get("page"),
            "chunk_id": metadata.get("chunk_id")
        })

    return {
        "answer": answer,
        "sources": sources,
        "search_query": results.get("search_query")
    }