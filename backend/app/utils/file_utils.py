# backend/app/utils/file_utils.py
"""
Small helpers for file saving/validation.
This file exposes a single async helper `save_uploaded_file` used by routes.
"""

import os
from fastapi import UploadFile
from typing import Tuple

async def save_uploaded_file(upload_file: UploadFile, file_id: str, upload_dir: str) -> Tuple[str, str]:
    """
    Save incoming UploadFile to disk with deterministic names:
      - {file_id}.pdf  (the original file)
      - {file_id}.txt  (the extracted-text preview path)
    Returns tuple (pdf_path, text_path).
    This function uses `await upload_file.read()` to read the uploaded bytes.
    """
    os.makedirs(upload_dir, exist_ok=True)

    pdf_filename = f"{file_id}.pdf"
    text_filename = f"{file_id}.txt"

    pdf_path = os.path.join(upload_dir, pdf_filename)
    text_path = os.path.join(upload_dir, text_filename)

    # Read bytes from the UploadFile and persist to disk
    content = await upload_file.read()
    with open(pdf_path, "wb") as f:
        f.write(content)

    # We do not write the text file here — pdf_service will create it after extraction.
    return pdf_path, text_path
