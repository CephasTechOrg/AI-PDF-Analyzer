import os
from docx import Document

def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from a Word (.docx) file.
    """
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return "\n".join(full_text).strip() or "⚠️ No extractable text found in DOCX."
    except Exception as e:
        raise RuntimeError(f"Error extracting DOCX: {e}")
