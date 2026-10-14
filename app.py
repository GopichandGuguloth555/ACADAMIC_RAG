"""Academic RAG Streamlit application."""
from pathlib import Path
import logging
import os
import streamlit as st
from config import CHUNK_OVERLAP, CHUNK_SIZE, GEMINI_MODEL, UPLOAD_DIR, ensure_data_dirs
from services.chunker import chunk_pages
from services.pdf_processor import extract_pdf, PDFProcessingError
from services.vector_store import VectorStore
from services.rag_service import RAGService
from services.llm_service import GeminiService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Academic RAG", page_icon="📚", layout="wide")
st.markdown("""<style>
:root {color-scheme:dark}
.stApp,[data-testid="stAppViewContainer"] {background:#11191a;color:#e5eeee}
[data-testid="stHeader"] {background:rgba(17,25,26,.92)}
.block-container {max-width:1420px;padding:1.25rem 2.2rem 2rem}
[data-testid="stSidebar"] {background:#172122;border-right:1px solid #293738}
[data-testid="stSidebar"] > div:first-child {padding-top:1.1rem}
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:#eff7f5}
.brand {display:flex;align-items:center;gap:.6rem;color:#edf8f5;font-size:1.05rem;font-weight:700;padding:.2rem .35rem 1.2rem}
.brand-mark {display:inline-flex;width:1.8rem;height:1.8rem;align-items:center;justify-content:center;border-radius:.55rem;background:#45c9a8;color:#10201c}
.nav-active {padding:.62rem .75rem;background:#233333;border:1px solid #304444;border-radius:.65rem;color:#eaf7f3;margin:0 0 1.2rem;font-size:.92rem}
.page-title {display:flex;align-items:center;justify-content:space-between;gap:1rem;margin:.3rem 0 1.1rem}
.page-title h1 {font-size:1.65rem;letter-spacing:-.025em;margin:0;color:#f1f6f5}
.page-subtitle {color:#9badab;font-size:.88rem;margin-top:.35rem}
.status-pill {display:inline-flex;align-items:center;gap:.45rem;color:#b9eadb;background:#19312d;border:1px solid #285047;border-radius:999px;padding:.38rem .7rem;font-size:.76rem;white-space:nowrap}
.hero {padding:1.4rem 1.6rem;background:#192425;border:1px solid #2a3a3b;border-radius:14px;margin:1rem 0 1.4rem;color:#dce8e6}
.hero h2 {color:#eff7f5;margin:.15rem 0 .5rem;font-size:1.35rem}
.hero p {color:#a9bcba;margin:0;line-height:1.65}
.stButton>button,.stFormSubmitButton>button {border-radius:9px;border:1px solid #344748;background:#202e2f;color:#dce9e7;transition:all .15s ease}
.stButton>button:hover,.stFormSubmitButton>button:hover {border-color:#45c9a8;color:#f4fffc}
.stFormSubmitButton>button[kind="primary"] {background:#45c9a8;border-color:#45c9a8;color:#10201c;font-weight:650}
[data-testid="stFileUploaderDropzone"] {background:#1b292a;border:1px dashed #405454;border-radius:10px}
[data-testid="stFileUploaderDropzone"]:hover {border-color:#45c9a8}
[data-testid="stTextInputRootElement"] {background:#1b292a;border-color:#344748;border-radius:10px}
[data-testid="stTextInputRootElement"] input {color:#eaf2f1}
[data-testid="stChatMessage"] {background:#192425;border:1px solid #2a3a3b;border-radius:13px;padding:.9rem 1rem;margin:.75rem 0}
[data-testid="stExpander"] {background:#192425;border:1px solid #2a3a3b;border-radius:10px}
[data-testid="stForm"] {background:#192425;border:1px solid #2a3a3b;border-radius:13px;padding:.55rem .65rem}
[data-testid="stMetric"] {background:#192425;border:1px solid #2a3a3b;border-radius:10px;padding:.7rem}
[data-testid="stCaptionContainer"] {color:#98aaa8}
hr {border-color:#2a393a}
@media (max-width:700px) {.block-container {padding:.8rem .8rem 1.4rem}.page-title h1 {font-size:1.4rem}.status-pill {font-size:.68rem}}
</style>""", unsafe_allow_html=True)

ensure_data_dirs()
@st.cache_resource
def get_store():
    return VectorStore()
store = get_store()
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown("<div class='brand'><span class='brand-mark'>✦</span> Academic RAG</div>", unsafe_allow_html=True)
    st.markdown("<div class='nav-active'>◉ &nbsp; RAG Chat</div>", unsafe_allow_html=True)
    st.header("Documents")
    if not os.getenv("GEMINI_API_KEY"):
        st.info("Add GEMINI_API_KEY to your .env file to enable answer generation.")
    uploads = st.file_uploader("Upload academic PDFs", type=["pdf"], accept_multiple_files=True, help="Text PDFs are supported. Scanned PDFs need OCR before upload.")
    if uploads:
        if st.button("Index uploaded PDFs", type="primary", use_container_width=True):
            progress = st.progress(0)
            for i, upload in enumerate(uploads):
                try:
                    parsed = extract_pdf(upload.getvalue(), upload.name)
                    if store.document_exists(parsed.document_id):
                        st.info(f"{parsed.filename} is already indexed.")
                    else:
                        chunks = chunk_pages(parsed.pages, parsed.document_id, parsed.filename, CHUNK_SIZE, CHUNK_OVERLAP)
                        with st.spinner(f"Embedding {parsed.filename}…"):
                            store.add_document(parsed.document_id, chunks)
                        (UPLOAD_DIR / f"{parsed.document_id}.pdf").write_bytes(upload.getvalue())
                        st.success(f"Indexed {parsed.filename} ({len(parsed.pages)} pages, {len(chunks)} chunks).")
                except PDFProcessingError as exc:
                    st.error(f"{upload.name}: {exc}")
                except Exception as exc:
                    logger.exception("PDF indexing failed")
                    st.error(f"Could not index {upload.name}: {exc}")
                progress.progress((i + 1) / len(uploads))
            st.rerun()

    docs = store.list_documents()
    st.caption(f"{len(docs)} indexed document{'s' if len(docs) != 1 else ''}")
    if not docs:
        st.info("No documents yet. Upload a text PDF to get started.")
    for item in docs:
        with st.container(border=True):
            st.markdown(f"**{item['filename']}**")
            st.caption(f"{item['chunks']} searchable chunks")
            if st.button("Delete", key=f"delete-{item['document_id']}"):
                try:
                    store.delete_document(item["document_id"])
                    stored = (UPLOAD_DIR / f"{item['document_id']}.pdf").resolve()
                    if stored.parent == UPLOAD_DIR.resolve() and stored.exists():
                        stored.unlink()
                    st.success(f"Deleted {item['filename']}.")
                    st.rerun()
                except Exception:
                    logger.exception("Document deletion failed")
                    st.error("Could not delete this document. Check the local data directory permissions.")
    if docs:
        if st.button("Clear all documents", use_container_width=True):
            st.session_state.confirm_clear = True
        if st.session_state.get("confirm_clear"):
            st.warning("This removes every indexed document and stored PDF.")
            left, right = st.columns(2)
            if left.button("Confirm clear all", type="primary"):
                try:
                    store.clear()
                    for path in UPLOAD_DIR.glob("*.pdf"):
                        if path.parent.resolve() == UPLOAD_DIR.resolve():
                            path.unlink()
                    st.session_state.confirm_clear = False
                    st.session_state.messages = []
                    st.rerun()
                except Exception:
                    logger.exception("Clear all failed")
                    st.error("Could not clear the document collection.")
            if right.button("Cancel"):
                st.session_state.confirm_clear = False
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.markdown(
    f"<div class='page-title'><div><h1>RAG Chat</h1><div class='page-subtitle'>Ask questions grounded in your academic PDFs, with page-level citations.</div></div><span class='status-pill'>● &nbsp; {len(docs)} source{'s' if len(docs) != 1 else ''} indexed</span></div>",
    unsafe_allow_html=True,
)

if not docs:
    st.markdown("<div class='hero'><h2>Welcome to your academic assistant</h2><p>Upload research papers, lecture notes, or other text-based academic PDFs in the sidebar. Then ask questions and inspect the supporting page citations.</p></div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Accept the older RAG response shape too, so an in-progress session
        # survives a hot reload after updating this app.
        st.markdown(message.get("content", message.get("answer", "")))
        for source in message.get("sources", []):
            label = f"{source['filename']} · page {source['page']}"
            with st.expander(label):
                st.caption(f"Citation: [{source['filename']}, p. {source['page']}]")
                st.write(source["text"])

if not docs:
    st.caption("Index at least one PDF to enable questions.")
with st.form("question-form", clear_on_submit=True):
    prompt_col, send_col = st.columns([1, 0.075], gap="small", vertical_alignment="bottom")
    with prompt_col:
        question = st.text_input(
            "Ask an academic question", label_visibility="collapsed",
            placeholder="Ask about your sources…",
        )
    with send_col:
        submitted = st.form_submit_button("➤", type="primary", disabled=not docs, help="Send question")
if submitted:
    if not question.strip():
        st.warning("Enter a question first.")
    else:
        st.session_state.messages.append({"role": "user", "content": question.strip()})
        try:
            with st.spinner("Searching your documents and generating an answer…"):
                result = RAGService(store, GeminiService(model=GEMINI_MODEL)).ask(question)
            st.session_state.messages.append({
                "role": "assistant", "content": result["answer"], "sources": result["sources"]
            })
        except Exception as exc:
            logger.exception("Question answering failed")
            st.session_state.messages.append({"role": "assistant", "content": f"I couldn't answer that right now. {exc}", "sources": []})
        st.rerun()
