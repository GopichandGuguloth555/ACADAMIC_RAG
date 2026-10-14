import fitz
import pytest
from services.pdf_processor import extract_pdf, PDFProcessingError

def make_pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data

def test_extracts_text_and_one_based_pages():
    result = extract_pdf(make_pdf("A study of memory."), "study.pdf")
    assert result.filename == "study.pdf"
    assert result.pages[0]["page"] == 1
    assert "memory" in result.pages[0]["text"]
    assert len(result.document_id) == 64

def test_rejects_empty_or_non_text_pdf():
    with pytest.raises(PDFProcessingError, match="empty"):
        extract_pdf(b"", "empty.pdf")
    doc = fitz.open()
    doc.new_page()
    data = doc.tobytes()
    with pytest.raises(PDFProcessingError, match="No extractable text"):
        extract_pdf(data, "scan.pdf")

def test_rejects_invalid_file():
    with pytest.raises(PDFProcessingError, match="corrupted"):
        extract_pdf(b"not a pdf", "x.pdf")
