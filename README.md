# Academic RAG

A local Streamlit application for searching academic PDFs and asking evidence-grounded questions. PDF text and embeddings stay in the project directory. Google Gemini is used only for answer generation; local Sentence Transformers create embeddings.

## Requirements

- Python 3.11 or 3.12 recommended (Python 3.13/3.14 dependency wheel availability can vary).
- Linux/Fedora build tools only if pip needs to compile a dependency.
- A Gemini API key for generated answers. Indexing and retrieval do not need a Gemini key.

## Install on Linux/Fedora

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# CPU-only PyTorch avoids downloading CUDA libraries on Linux/Fedora.
python -m pip install --index-url https://download.pytorch.org/whl/cpu 'torch==2.14.1+cpu'
python -m pip install -r requirements.txt
cp .env.example .env
```

Set `GEMINI_API_KEY` in `.env` to a key from Google AI Studio. The app never displays or logs the key. `GEMINI_MODEL` defaults to `gemini-3.5-flash-lite`; `GEMINI_MODEL` and `EMBEDDING_MODEL` can be overridden in `.env`.

## Run

```bash
source .venv/bin/activate
streamlit run app.py
```

Upload one or more text-based PDFs in the sidebar and choose **Index uploaded PDFs**. Ask questions in the main pane; expand the source cards to inspect the exact excerpt and page. Use document-level delete or **Clear all documents** in the sidebar. **Clear conversation** only clears the current browser session's chat history.

The first indexing request downloads the local embedding model and can take a little while. This model is cached for the Streamlit process and reused. Scanned or image-only PDFs need OCR before upload. Identical PDF contents are recognized by SHA-256 and will not be indexed twice, even if uploaded under a different name.

## Data and privacy

`data/uploads/` holds local copies and `data/chroma/` holds the persistent vector index. Both start empty and are excluded from version control. Deleting a document removes its chunks and local PDF. No remote vector database is used. Retrieved excerpts and questions are sent to the configured Gemini API when an answer is requested.

## Tests

```bash
source .venv/bin/activate
pytest -q
```

Tests use temporary Chroma databases, synthetic PDFs, and fake embeddings/LLM responses. They do not make paid API calls.

## Limitations

- Text extraction uses PyMuPDF and does not perform OCR.
- Similarity retrieval uses a bounded top-five cosine search. Very short queries or specialized terminology may need a more explicit question.
- Gemini availability depends on a valid key, network access, quota, and the selected model being enabled for the account.
