from sqlalchemy import text
from sqlalchemy.orm import Session
from query import DENSE_SEARCH_QUERY, SPARSE_SEARCH_QUERY


class DocumentRepository():

    def __init__(self, db: Session) -> None:
        self.db = db

    
    async def get_dense_search_results(self):
        return self.db.execute(text(DENSE_SEARCH_QUERY))

    async def get_sparse_search_results(self):
        return self.db.execute(text(SPARSE_SEARCH_QUERY))

        