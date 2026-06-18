from fastapi import Depends
from db import get_db
from repository import DocumentRepository
from services.document_service import DocumentService
from clients.redis_client import r

def get_document_service(db = Depends(get_db)):
    repo = DocumentRepository(db)
    return DocumentService(repo, r)
