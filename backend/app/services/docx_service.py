"""
Service for extracting text from DOCX files.
This file parallels pdf_service.py but for Word documents.
"""

from docx import Document


def extract_text_from_docx(docx_path: str) -> str:
    """
    Extract text from a DOCX file and return as a single string.
    - Reads paragraphs in order.
    - Joins them with newlines.
    """
    try:
        doc = Document(docx_path)
        text_chunks = []

        for para in doc.paragraphs:
            if para.text.strip():  # ignore empty lines
                text_chunks.append(para.text.strip())

        extracted_text = "\n".join(text_chunks)
        return extracted_text if extracted_text else "⚠️ No extractable text found in DOCX."

    except Exception as e:
        raise RuntimeError(f"Failed to read DOCX: {e}")
