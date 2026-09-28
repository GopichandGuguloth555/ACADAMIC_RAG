from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)

    # Add useful metadata to every chunk
    for index, chunk in enumerate(chunks):
        source = chunk.metadata.get("source", "")
        page = chunk.metadata.get("page", 0)

        chunk.metadata["document_name"] = source.split("/")[-1]
        chunk.metadata["page"] = page + 1
        chunk.metadata["chunk_id"] = index

    return chunks