from retrieval import retrieve_documents
from llm import generate_answer


def answer_question(query: str, k: int = 5):

    # 1. Retrieve relevant documents
    results = retrieve_documents(query, k=k)

    documents = results["documents"]
    metadatas = results["metadatas"]

    # 2. Build context
    context_parts = []
    sources = []

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas),
        start=1
    ):
        context_parts.append(
            f"[Source {i}]\n{document}"
        )

        sources.append({
            "source": metadata.get("source"),
            "page": metadata.get("page")
        })

    context = "\n\n".join(context_parts)

    # 3. Create RAG prompt
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

    # 4. Generate answer using LLM
    answer = generate_answer(prompt)

    # 5. Return answer + sources
    return {
        "answer": answer,
        "sources": sources
    }