# Create retrieval config object

from pydantic import BaseModel

class BM25Config(BaseModel):
    """BM25 retriever configuration"""
    k1: float = 1.5
    b: float = 0.75

class RetrieverConfig(BaseModel):
    """Hybrid retrieval thresholds"""
    top_k: int = 10
    rerank_top_n: int = 5
    bm25_weight: float = 0.3
    vector_weight: float = 0.7