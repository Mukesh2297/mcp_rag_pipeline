from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services import DocumentService
from dependencies import get_document_service


class Query(BaseModel):
    question: str

router = APIRouter()

@router.post("/get_answer")
async def get_answer(payload: Query, document_service: DocumentService = Depends(get_document_service)):
    return await document_service.get_response(payload.question)

    