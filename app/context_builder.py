def build_context(documents, metadatas, max_chars=12000):
    """
    Build a clean, compact context for the LLM.

    Removes duplicate chunks and prevents the context
    from becoming unnecessarily large.
    """

    context_parts = []
    seen = set()
    current_length = 0

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas),
        start=1
    ):

        # Remove duplicate chunks
        normalized_document = document.strip()

        if normalized_document in seen:
            continue

        seen.add(normalized_document)

        document_name = metadata.get(
            "document_name",
            "Unknown document"
        )

        page = metadata.get(
            "page",
            "Unknown page"
        )

        chunk_id = metadata.get(
            "chunk_id",
            "Unknown"
        )

        source = (
            f"[Source {i}]\n"
            f"Document: {document_name}\n"
            f"Page: {page}\n"
            f"Chunk ID: {chunk_id}\n\n"
        )

        source += document.strip()

        # Don't exceed context limit
        if current_length + len(source) > max_chars:
            break

        context_parts.append(source)
        current_length += len(source)

    return "\n\n---\n\n".join(context_parts)