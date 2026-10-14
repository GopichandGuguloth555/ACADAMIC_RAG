"""Safe PDF text extraction."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
import pymupdf as fitz

class PDFProcessingError(ValueError):
    """The input is not a usable text PDF."""

@dataclass(frozen=True)
class ExtractedPDF:
    filename: str
    document_id: str
    pages: list[dict[str, int | str]]
    sha256: str

def extract_pdf(data: bytes, filename: str) -> ExtractedPDF:
    if not filename.lower().endswith(".pdf"):
        raise PDFProcessingError("Only PDF files can be indexed.")
    if not data:
        raise PDFProcessingError("The uploaded PDF is empty.")
    digest = hashlib.sha256(data).hexdigest()
    safe_name = Path(filename).name
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            if doc.is_encrypted:
                raise PDFProcessingError("This PDF is encrypted. Remove its password and try again.")
            pages = [{"page": n + 1, "text": page.get_text("text")} for n, page in enumerate(doc)]
    except PDFProcessingError:
        raise
    except (fitz.FileDataError, RuntimeError, ValueError) as exc:
        raise PDFProcessingError("This file is corrupted or is not a valid PDF.") from exc
    if not any(str(page["text"]).strip() for page in pages):
        raise PDFProcessingError("No extractable text was found. Scanned PDFs need OCR before indexing.")
    return ExtractedPDF(safe_name, digest, pages, digest)
