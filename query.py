DENSE_SEARCH_QUERY = """
    SELECT
        id,
        content,
        1 - (embedding <=> CAST(:query_embedding AS vector)) AS score
    FROM documents
    ORDER BY embedding <=> CAST(:query_embedding AS vector)
    LIMIT :top_k
"""


SPARSE_SEARCH_QUERY = """
    select id, content, ts_rank(tsv, plainto_tsquery('english', :query)) as score
    from documents
    where tsv @@ plainto_tsquery('english', :query)
    order by score desc
    limit :top_k
"""

__all__ = ["DENSE_SEARCH_QUERY", "SPARSE_SEARCH_QUERY"]