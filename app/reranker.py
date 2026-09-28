from sentence_transformers import CrossEncoder


model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank_documents(query, documents, metadatas, top_k=5):

    pairs = [
        (query, document)
        for document in documents
    ]

    scores = model.predict(pairs)

    ranked = sorted(
        zip(documents, metadatas, scores),
        key=lambda x: x[2],
        reverse=True
    )

    return ranked[:top_k]