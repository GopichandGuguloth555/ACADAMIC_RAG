from retrieval import retrieve_documents
from llm import generate_answer
from context_builder import build_context


def answer_question(query: str, k: int = 5):

    # 1. Retrieve and rerank relevant documents
    results = retrieve_documents(query, k=k)

    documents = results["documents"]
    metadatas = results["metadatas"]

    # 2. Build optimized context
    context = build_context(
        documents,
        metadatas
    )

    # 3. Create grounded RAG prompt
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

    # 4. Generate answer using the LLM
    answer = generate_answer(prompt)

    # 5. Prepare source information
    sources = []

    for metadata in metadatas:
        sources.append({
            "document": metadata.get("document_name"),
            "page": metadata.get("page"),
            "chunk_id": metadata.get("chunk_id")
        })

    # 6. Return complete RAG result
    return {
        "answer": answer,
        "sources": sources,
        "search_query": results.get("search_query"),
        "context": context
    }