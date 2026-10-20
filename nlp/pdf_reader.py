"""
Secure PDF Reader and Validator for CareerMatch AI.
Validates PDF headers, bounds, and extracts clean textual content.
"""

import io
from typing import Dict, Any, Tuple
import pypdf


MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit


class PDFProcessingError(Exception):
    """Raised when PDF reading fails or security checks trigger."""
    pass


def validate_pdf_bytes(pdf_bytes: bytes, filename: str = "resume.pdf") -> None:
    """Performs rigorous security and format validation on incoming PDF bytes."""
    if not pdf_bytes:
        raise PDFProcessingError("Uploaded file is empty.")

    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise PDFProcessingError(f"File size exceeds 10MB limit ({len(pdf_bytes) / 1024 / 1024:.2f} MB).")

    # Magic byte check: must start with %PDF-
    if not pdf_bytes.startswith(b"%PDF-"):
        raise PDFProcessingError("Invalid file signature. File is not a valid PDF document.")


def extract_text_from_pdf(pdf_bytes: bytes, filename: str = "resume.pdf") -> Tuple[str, Dict[str, Any]]:
    """
    Safely parses PDF bytes and extracts text across all pages.
    Returns (extracted_text, metadata).
    """
    validate_pdf_bytes(pdf_bytes, filename)

    try:
        stream = io.BytesIO(pdf_bytes)
        reader = pypdf.PdfReader(stream)

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise PDFProcessingError("Password-protected PDFs cannot be analyzed. Please upload an unprotected PDF.")

        page_count = len(reader.pages)
        if page_count == 0:
            raise PDFProcessingError("PDF contains zero pages.")

        extracted_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            extracted_pages.append(page_text.strip())

        full_text = "\n\n".join(extracted_pages).strip()

        if len(full_text) < 50:
            raise PDFProcessingError(
                "PDF contains insufficient text. If this is a scanned or image-only document, "
                "please provide a text-searchable PDF."
            )

        metadata = {
            "page_count": page_count,
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
            "filename": filename
        }

        return full_text, metadata

    except PDFProcessingError:
        raise
    except Exception as e:
        raise PDFProcessingError(f"Failed to parse PDF document: {str(e)}")
