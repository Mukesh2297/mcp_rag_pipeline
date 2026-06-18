from sqlalchemy import select, text
from sqlalchemy.orm import Session
from models import Document
from query import DENSE_SEARCH_QUERY, SPARSE_SEARCH_QUERY
from clients import encode_one
from clients.redis_client import redis


class DocumentRepository():

    def __init__(self, db: Session) -> None:
        self.db = db
    
    async def get_dense_search_results(self, query: str, top_k):
        query_embedding = await encode_one(query)
        return self.db.execute(text(DENSE_SEARCH_QUERY), {"query_embedding": query_embedding, "top_k": top_k}).fetchall()

    async def get_sparse_search_results(self, query: str, top_k):
        return self.db.execute(text(SPARSE_SEARCH_QUERY), {"query": query, "top_k": top_k}).fetchall()

    async def get_all_documents(self):
        result = self.db.execute(select(Document.id, Document.content))
        return result.mappings().all()

        