import re
from sqlalchemy import text
from sqlalchemy.orm import Session
from models import Document
from dotenv import load_dotenv
import os
from openai import OpenAI
import numpy as np
from datasets import load_dataset
from query import DENSE_SEARCH_QUERY, SPARSE_SEARCH_QUERY

load_dotenv()

LLM_LOCALHOST_URL = os.getenv("LLM_LOCALHOST_URL")
DATASET_URL = os.getenv("DATASET_URL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
CACHE_PATH = os.getenv("CACHE_PATH")
CHAT_COMPLETIONS_MODEL = os.getenv("CHAT_COMPLETIONS_MODEL")

client = OpenAI(base_url=LLM_LOCALHOST_URL, api_key='not available')

def dense_search(query_embedding, db: Session, top_k: int = 20):
    try:
        return db.execute(text(DENSE_SEARCH_QUERY), {"query_embedding": query_embedding, "top_k": top_k}).fetchall()
    except Exception as e:
        print(e)
        return []

def sparse_search(query: str, db: Session, top_k: int = 20):
    try:
        return db.execute(text(SPARSE_SEARCH_QUERY), {"query": query, "top_k": top_k}).fetchall()
    except Exception as e:
        print(e)
        return []

def process_data():
    ds = load_dataset(DATASET_URL, split="train")

    contexts = []
    contexts_seen = set()
    for row in ds:
        if row["context"] not in contexts_seen:
            contexts_seen.add(row["context"])
            contexts.append(row["context"])
    return contexts

def encode_one(sentence: str) -> list[float]:
    response = client.embeddings.create(
        input=sentence,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding

def already_seeded(db: Session) -> bool:
    return len(db.query(Document).all()) > 0


def hybrid_search(query: str, db: Session, top_k: int) -> list[dict]:
    query_embedding = encode_one(query)

    dense_results: list[Document] = dense_search(query_embedding, db, top_k)

    sparse_results: list[Document] = sparse_search(query, db, top_k)

    dense_ranks = {row.id: idx + 1 for idx, row in enumerate(dense_results)}
    sparse_ranks = {row.id: idx + 1 for idx, row in enumerate(sparse_results)}

    all_results = set(dense_ranks.keys()) | set(sparse_ranks.keys())

    K = 60   # RRF constant
    scored = []
    for id in all_results:
        dense_score  = 1 / (K + dense_ranks[id])  if id in dense_ranks  else 0
        sparse_score = 1 / (K + sparse_ranks[id]) if id in sparse_ranks else 0
        rrf_score    = dense_score + sparse_score

        context = next(
            r.content for r in list(dense_results) + list(sparse_results)
            if r.id == id
        )

        scored.append({
            "id":      id,
            "context": context,
            "score":   rrf_score
        })
    
    scored.sort(key=lambda x : x['score'], reverse=True)
    
    return scored[:top_k]


def get_llm_response(prompt):
    response = client.chat.completions.create(messages = [{'role': 'system', 'content': prompt}], model=CHAT_COMPLETIONS_MODEL)
    return response.choices[0].message.content



def get_response(query:str, db: Session, top_k: int = 20) -> str:
    top_score_docs: list[dict] = hybrid_search(query=query, db=db, top_k=top_k)
    prompt = f"""
    {query}

    For the above question, answer based on the below retrieved contexts. 
    The retrieved contexts is scored based on the hybrid calculation of dense and spare search,
    so do your evaluation based on the score and answer accordingly. Give me crisp answer, dont be elaborate. If you can't evaluate the answer, please say 'Unable to find answer'

    {top_score_docs}
    """

    answer = get_llm_response(prompt)

    return answer

