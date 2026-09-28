from query_rewriter import rewrite_query


queries = [
    "What is computer science?",
    "What does it mean?",
    "Explain algorithms in simple terms"
]


for query in queries:

    rewritten = rewrite_query(query)

    print("\nOriginal:")
    print(query)

    print("\nRewritten:")
    print(rewritten)

    print("-" * 60)