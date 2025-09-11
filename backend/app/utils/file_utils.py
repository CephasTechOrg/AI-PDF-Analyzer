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
      - {file_id}.ext  (the original file, keeping extension: pdf or docx)
      - {file_id}.txt  (the extracted-text preview path)
    Returns tuple (file_path, text_path).
    This function uses `await upload_file.read()` to read the uploaded bytes.
    """
    os.makedirs(upload_dir, exist_ok=True)

    # Keep the original extension (.pdf, .docx, etc.)
    _, ext = os.path.splitext(upload_file.filename)
    ext = ext.lower()

    if ext not in [".pdf", ".docx"]:
        raise ValueError(f"Unsupported file extension: {ext}")

    file_filename = f"{file_id}{ext}"
    text_filename = f"{file_id}.txt"

    file_path = os.path.join(upload_dir, file_filename)
    text_path = os.path.join(upload_dir, text_filename)

    # Read bytes from the UploadFile and persist to disk
    content = await upload_file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # We do not write the text file here — pdf_service/docx_service will create it after extraction.
    return file_path, text_path
