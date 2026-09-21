# Manage long term memory

from sqlalchemy import text
from app.db import get_db_session
from app.config import config
from app.observability.logger import get_logger
from app.embedding import get_embedder

logger = get_logger(__name__)

# Format vector
def _format_vector(embedding: list[float]) -> str:
    """Turn to the format of pgvector: [0.1,0.2,...] - no whitespace"""
    return "[" + ",".join(str(v) for v in embedding) + "]"

# Save long term 
def save_long_term_memory(session_id: str, topic_summary: str, 
                          importance_score: float, source_trace_id: str) -> None:
    """Embedding topic_summary and then save to long-term memory"""
    from app.db.models import ConversationLongTerm

    embedding = get_embedder().embed_query(topic_summary)   # get embedding of topic_summary

    with get_db_session() as session:
        row = ConversationLongTerm(
            session_id=session_id,
            topic_summary=topic_summary,
            embedding=embedding,
            importance_score=importance_score,
            source_trace_id=source_trace_id
        )
        session.add(row)
        session.commit()

    logger.info(f"Bộ nhớ long-term đã được lưu: session = {session_id}, topic = {topic_summary[:60]!r}")

# Search long term
def search_long_term_memory(session_id: str, query_text: str) -> list[dict]:
    """Semantic search for long-term memory similarity with query"""
    query_embedding = get_embedder().embed_query(query_text)
    top_k = config.memory.long_term_top_k
    threshold = config.memory.long_term_similarity_threshold

    with get_db_session() as session :
        stmt = text("""
            SELECT id, topic_summary, importance_score, created_at,
                1 - (embedding <=> :query_embedding) AS similarity
            FROM conversation_long_term
            WHERE session_id = :session_id
            ORDER BY embedding <=> :query_embedding
            LIMIT :top_k
        """)    # get top k embedding vectors which are similarity with query embedding 
        rows = session.execute(
            stmt,
            {
                "query_embedding": _format_vector(query_embedding),
                "session_id": session_id,
                "top_k": top_k
            }
        ).fetchall()

    return [
        {
            "topic": row.topic_summary,
            "summary": row.topic_summary,
            "embedding_id": row.id,
            "similarity": round(row.similarity, 4),
            "timestamp": row.created_at.isoformat()
        }
        for row in rows
        if row.similarity >= threshold
    ]