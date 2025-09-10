import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader  # ✅ for extracting text from PDFs

app = FastAPI()

# Folder to save uploads
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # generate unique file_id
    file_id = str(uuid.uuid4())

    # save original PDF
    pdf_filename = f"{file_id}.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # extract text from PDF
    text_filename = f"{file_id}.txt"
    text_path = os.path.join(UPLOAD_DIR, text_filename)

    try:
        reader = PdfReader(pdf_path)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text() or ""  # handle blank pages

        # Save extracted text to a .txt file
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(extracted_text.strip() or "⚠️ No extractable text found in PDF.")

        pages_indexed = len(reader.pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {e}")

    return {
        "status": "ok",
        "file_id": file_id,
        "filename": file.filename,
        "pages_indexed": pages_indexed,
        "message": f"Saved to {pdf_path} (preview: {text_path})"
    }


@app.get("/api/pdf/{file_id}/text")
async def get_pdf_text(file_id: str):
    text_path = os.path.join(UPLOAD_DIR, f"{file_id}.txt")
    if not os.path.exists(text_path):
        raise HTTPException(status_code=404, detail="Text preview not found for this file")

    with open(text_path, "r", encoding="utf-8") as f:
        content = f.read()

    return {"file_id": file_id, "text": content}
