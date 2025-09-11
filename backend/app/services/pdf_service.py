# backend/app/services/pdf_service.py
"""
PDF extraction service.
Contains the logic to read a PDF from disk, extract text and save preview.
"""

import os
from typing import Tuple
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path: str, text_path: str) -> Tuple[str, int]:
    """
    Read `pdf_path`, extract text from each page, write to `text_path`.
    Returns (extracted_text, pages_count).
    - Uses PyPDF2.PdfReader which works well for selectable text PDFs.
    - If no extractable text is found, we write a small warning message to the .txt.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages_count = len(reader.pages)
    pieces = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            # If a page fails, continue and include an empty placeholder
            page_text = ""
        if page_text.strip():
            pieces.append(page_text.strip())

    # Join pages with double newlines to preserve basic separation
    content = "\n\n".join(pieces).strip()
    if not content:
        content = "⚠️ No extractable text found in PDF."

    # make sure directory exists and write preview
    os.makedirs(os.path.dirname(text_path) or ".", exist_ok=True)
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content, pages_count
