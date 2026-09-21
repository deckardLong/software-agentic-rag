# Wrapper sentence transformers - Long-term memory + RAG retrieval

from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from app.config import config

# Get embedder
@lru_cache(maxsize=1)
def get_embedder() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=config.embedding.model_name,
        model_kwargs={"device": config.embedding.device},
        encode_kwargs={"batch_size": config.embedding.batch_size}
    )