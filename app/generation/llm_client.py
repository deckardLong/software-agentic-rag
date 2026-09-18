# Wrapper for LLM model (Dev)

from functools import lru_cache
from langchain_ollama import ChatOllama
from app.config import config

# Get LLM model (Ollama)
@lru_cache(maxsize=1)
def get_generation_llm() -> ChatOllama:
    """LLM for Domain Classifier, Generation, and Query Rewrite"""
    return ChatOllama(
        model=config.llm_generation.model_name,
        base_url=config.llm_generation.base_url,
        temperature=config.llm_generation.temperature,
        timeout=config.llm_generation.timeout_seconds
    )