from repository import DocumentRepository
from clients import get_llm_response
import json
from core.logging import *
import logging

log = logging.getLogger(__name__)


class DocumentService():

    def __init__(self, documentRepository: DocumentRepository, redis_client) -> None:
        print("Document Service injected")
        self.document_repository = documentRepository
        self.redis = redis_client

    async def get_all_documents(self):
        cached = await self.redis.get("all_docs")
        if cached:
            log.info("Cache HIT: all_docs")
            return json.loads(cached)
        log.info("Cache MISS: all_docs — fetching from DB")
        docs = await self.document_repository.get_all_documents()
        serialized = [{'id': doc.id, 'content': doc.content} for doc in docs]
        try:
            await self.redis.set("all_docs", json.dumps(serialized), ex=300)
            log.info("Cache SET: all_docs")
        except Exception:
            log.exception(msg='Failed to cache response')
        return serialized

    async def get_dense_search_results(self, query: str, top_k: int):
        return await self.document_repository.get_dense_search_results(query=query, top_k=top_k)

    async def get_sparse_results(self, query: str, top_k = 20):
        return await self.document_repository.get_sparse_search_results(query=query, top_k=top_k)
    
    async def hybrid_search(self, query: str, top_k = 20) -> list[dict]:
        dense_results = await self.get_dense_search_results(query=query, top_k=top_k)

        sparse_results = await self.get_sparse_results(query=query, top_k=top_k)
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

    async def get_response(self, query:str, top_k: int = 20):
        top_score_docs: list[dict] = await self.hybrid_search(query=query, top_k=top_k)
        prompt = f"""
        {query}

        For the above question, answer based on the below retrieved contexts. 
        The retrieved contexts is scored based on the hybrid calculation of dense and spare search,
        so do your evaluation based on the score and answer accordingly. Give me crisp answer, dont be elaborate. If you can't evaluate the answer, please say 'Unable to find answer'

        {top_score_docs}
        """

        answer = await get_llm_response(prompt)

        return answer


