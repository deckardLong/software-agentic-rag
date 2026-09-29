# Sematic search

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from sqlalchemy import select
from sqlalchemy.orm import defer
from app.db import get_db_session
from app.db.models import Chunk
from app.embedding import get_embedder
from app.rag.documents import chunk_to_document

# Define class
class PgVectorRetriever(BaseRetriever):
    """Cosine search in chunks table"""
    k: int = 10

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        query_embedding = get_embedder().embed_query(query)

        # get distance
        distance = Chunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(Chunk, distance.label("distance"))
            .options(defer(Chunk.embedding))
            .order_by(distance)
            .limit(self.k)
        )
        with get_db_session() as session:
            rows = session.execute(stmt).all()
            return [
                chunk_to_document(chunk, vector_score=1-dist)
                for chunk, dist in rows
            ]