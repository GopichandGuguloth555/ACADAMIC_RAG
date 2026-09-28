from llm import generate_answer


def rewrite_query(query: str) -> str:

    prompt = f"""
Rewrite the following user question into a clear,
specific search query for retrieving information
from academic documents.

Rules:
- Preserve the original meaning.
- Do not answer the question.
- Do not add facts that are not present in the question.
- Return only the rewritten query.

User question:
{query}

Rewritten search query:
"""

    rewritten_query = generate_answer(prompt)

    return rewritten_query.strip()