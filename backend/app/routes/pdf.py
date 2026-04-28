import os
import uuid
from typing import Optional

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from PyPDF2 import PdfReader

from app.services.vector_store import VectorStoreService

router = APIRouter()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append(f"--- Page {i + 1} ---\n{text}")
    return "\n\n".join(pages)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB",
        )

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        text = extract_text_from_pdf(file_path)
        if not text.strip():
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF. It may be image-based or empty.",
            )

        vector_service = VectorStoreService()
        vector_service.index_document(doc_id, text)

        page_count = len(PdfReader(file_path).pages)

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "page_count": page_count,
            "char_count": len(text),
            "status": "indexed",
        }
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@router.get("/documents")
async def list_documents():
    if not os.path.exists(UPLOAD_DIR):
        return {"documents": []}

    documents = []
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith(".pdf"):
            doc_id = filename.replace(".pdf", "")
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                reader = PdfReader(file_path)
                page_count = len(reader.pages)
                documents.append({"doc_id": doc_id, "page_count": page_count})
            except Exception:
                continue

    return {"documents": documents}


@router.delete("/{doc_id}")
async def delete_pdf(doc_id: str):
    vector_service = VectorStoreService()
    vector_service.remove_document(doc_id)

    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "deleted", "doc_id": doc_id}

    raise HTTPException(status_code=404, detail="Document not found")
