# Hybrid retriever (BM25 + Dense retriever)

from functools import lru_cache
from langchain_classic.retrievers import EnsembleRetriever
from app.agent.state import AgentState
from app.config import config
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.rag.documents import doc_to_dict
from app.rag.retriever.bm25_retriever import get_bm25_retriever
from app.rag.retriever.vector_retriever import PgVectorRetriever

logger = get_logger(__name__)

# Get hybrid retriever
@lru_cache(maxsize=1)
def get_hybrid_retriever() -> EnsembleRetriever:
    cfg = config.retriever
    return EnsembleRetriever(
        retrievers=[get_bm25_retriever(), PgVectorRetriever(k=cfg.top_k)],
        weights=[cfg.bm25_weight, cfg.vector_weight],
        id_key="chunk_id"   # dedup by chunk_id
    )

# Hybrid retrieve
@observe_node("hybrid_retrieval")
def hybrid_retrieve(state: AgentState) -> dict:
    """Handle hybrid search"""
    query = state.get("rewritten_query") or state["user_query"]
    docs = get_hybrid_retriever().invoke(query)[:config.retriever.top_k]

    logger.info(f"Truy xuất Hybrid: {len(docs)} tài liệu", 
                extra= {
                    "query": query,
                    "doc_count": len(docs)
                }
            )
    return {
        "retrieved_docs": [doc_to_dict(d) for d in docs],
        "retrieval_method": "hybrid"
    }