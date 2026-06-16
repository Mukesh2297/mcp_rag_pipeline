from sqlalchemy.orm import Session
from models import Document
from datasets import load_dataset
from core.config import settings

DATASET_URL = settings.DATASET_URL

def process_data():
    ds = load_dataset(DATASET_URL, split="train")

    contexts = []
    contexts_seen = set()
    for row in ds:
        if row["context"] not in contexts_seen:
            contexts_seen.add(row["context"])
            contexts.append(row["context"])
    return contexts



def already_seeded(db: Session) -> bool:
    return len(db.query(Document).all()) > 0



