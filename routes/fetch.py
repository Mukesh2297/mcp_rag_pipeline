from fastapi import APIRouter, Depends, HTTPException
from dependencies import get_document_service
from models import Document
from schemas import DocumentResponse
from core.logging import *
import logging

from services import DocumentService

log = logging.getLogger(__name__)

router = APIRouter()


@router.get("/documents")
async def get_all_documents(document_service: DocumentService = Depends(get_document_service)) -> list[dict]:
    log.info("Get documents invoked")
    try:
        return await document_service.get_all_documents()
    except Exception as e:
        log.exception("Failed to fetch documents")
        raise HTTPException(status_code=500,detail="Failed to fetch documents")
