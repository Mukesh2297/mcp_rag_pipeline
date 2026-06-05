from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Document
from pydantic import BaseModel
from services import get_response


class Query(BaseModel):
    question: str

router = APIRouter()

@router.post("/get_answer")
def get_answer(payload: Query, db: Session = Depends(get_db)):
    print(payload.question)
    return get_response(payload.question, db)

    