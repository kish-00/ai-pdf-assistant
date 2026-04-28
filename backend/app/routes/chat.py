from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.vector_store import VectorStoreService

router = APIRouter()


class ChatRequest(BaseModel):
    doc_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []
    doc_id: str


@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    vector_service = VectorStoreService()
    result = vector_service.query_document(request.doc_id, request.question)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found or not indexed. Please upload it first.",
        )

    return ChatResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
        doc_id=request.doc_id,
    )


@router.post("/summarize/{doc_id}")
async def summarize_document(doc_id: str):
    vector_service = VectorStoreService()
    result = vector_service.summarize_document(doc_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found or not indexed.",
        )

    return {"doc_id": doc_id, "summary": result}
