# backend/app/routes/upload.py
"""
Routes for uploading files and retrieving extracted text.
This file wires file_utils + pdf_service together.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.file_utils import save_uploaded_file
from app.services.pdf_service import extract_text_from_pdf

router = APIRouter()

# Upload directory (can be overridden with env var later)
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload a PDF, save it, extract text, and return metadata (file_id, pages_count).
    - Validates the extension (simple check).
    - Uses async save helper to persist binary.
    - Calls pdf_service to extract text and write preview file.
    """
    # Basic validation: check extension (MIME check could be added later)
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Generate stable file id (UUID)
    file_id = str(uuid.uuid4())

    # Persist the uploaded file and obtain paths
    pdf_path, text_path = await save_uploaded_file(file, file_id, UPLOAD_DIR)

    # Extract text (synchronous; if heavy, we can run in background in the future)
    try:
        extracted_text, pages_indexed = extract_text_from_pdf(pdf_path, text_path)
    except Exception as exc:
        # Keep error messages clean for the client
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {exc}")

    return {
        "status": "ok",
        "file_id": file_id,
        "filename": file.filename,
        "pages_indexed": pages_indexed,
        "message": f"Saved to {pdf_path} (preview: {text_path})"
    }


@router.get("/pdf/{file_id}/text")
async def get_pdf_text(file_id: str):
    """
    Return the full extracted text for a given file_id.
    The text file is named {file_id}.txt under UPLOAD_DIR.
    """
    text_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Text preview not found for this file")

    with open(text_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"file_id": file_id, "text": content}
