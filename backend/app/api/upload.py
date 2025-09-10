# backend/app/api/upload.py
"""
File upload endpoint for PDFs.

This endpoint:
- Accepts a multipart PDF upload
- Validates extension
- Saves the original PDF to `uploads/`
- Extracts text (per page) using pdfplumber and saves a .txt preview
- Returns basic metadata (file_id, pages_count, saved paths)

Why: early local parsing ensures we control the text extraction pipeline.
Later: we'll add OCR fallback (pdf2image + pytesseract) and chunking + embeddings.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import uuid
import os
import io
import pdfplumber
from typing import List

router = APIRouter()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

class UploadResponse(BaseModel):
    status: str
    file_id: str
    filename: str
    pages_indexed: int
    message: str = ""

@router.post("/upload-pdf", response_model=UploadResponse, tags=["upload"])
async def upload_pdf(file: UploadFile = File(...)):
    # Validate file type by extension (basic). In prod also check MIME type and file magic.
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Use a UUID prefix to avoid collisions and to create a stable file id
    file_id = str(uuid.uuid4())
    saved_filename = f"{file_id}_{os.path.basename(file.filename)}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)

    # Read bytes from UploadFile (Starlette / FastAPI handles streaming for large files)
    content = await file.read()
    # Saves the raw PDF to disk (keeps the original; we can re-process later)
    with open(saved_path, "wb") as f:
        f.write(content)

    # Extract text per page using pdfplumber (fast for text PDFs)
    pages_text: List[str] = []
    try:
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for p, page in enumerate(pdf.pages, start=1):
                # page.extract_text() returns None if no text was found on the page
                txt = page.extract_text() or ""
                pages_text.append(f"--- PAGE {p} ---\n{txt}")
    except Exception as exc:
        # If parsing fails, return a helpful message. We'll add OCR fallback later.
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {exc}")

    # Persist a lightweight text preview (useful for quick check during dev)
    preview_path = os.path.join(UPLOAD_DIR, f"{saved_filename}.txt")
    with open(preview_path, "w", encoding="utf-8") as pf:
        pf.write("\n\n".join(pages_text))

    return UploadResponse(
        status="ok",
        file_id=file_id,
        filename=saved_filename,
        pages_indexed=len(pages_text),
        message=f"Saved to {saved_path} (preview: {preview_path})"
    )
