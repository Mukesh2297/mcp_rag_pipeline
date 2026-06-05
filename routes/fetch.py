from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Document

router = APIRouter()


@router.get("/documents")
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(Document).all()