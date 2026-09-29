# Define reranker

from functools import lru_cache
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from app.agent.state import AgentState
from app.config import config
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Get cross encoder
@lru_cache(maxsize=1)
def get_cross_encoder() -> HuggingFaceCrossEncoder:
    return HuggingFaceCrossEncoder(
        model_name=config.retriever.reranker_model_name,
        model_kwargs={
            "device": config.embedding.device
        }
    )

# Rerank
@observe_node("reranker")
def rerank(state: AgentState) -> dict:
    """Handle reranker"""
    query = state.get("rewritten_query") or state["user_query"]
    docs = state.get("retrieved_docs", [])

    if not docs:
        return {
            "reranked_docs": []
        }

    # Scores
    scores = get_cross_encoder().score([(query, d["content"]) for d in docs])

    # Ranked
    ranked = sorted(zip(docs, scores), key=lambda pair: pair[1], reverse=True)  # largest to smallest

    # Top n
    top_n = ranked[:config.retriever.rerank_top_n]
    logger.info(f"Được xếp hạng (Reranked) {len(docs)} -> {len(top_n)} tài liệu")
    return {
        "reranked_docs": [{
            **doc, 
            "rerank_score": round(float(s), 4)}
            for doc, s in top_n
        ]
    }