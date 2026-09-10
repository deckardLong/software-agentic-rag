# Create master config object for all sub-configs

from pydantic import BaseModel
from app.config.models.llm import OllamaConfig, GeminiConfig
from app.config.models.embedding import EmbeddingConfig
from app.config.models.database import PostgreSQLConfig
from app.config.models.retriever import BM25Config, RetrieverConfig
from app.config.models.grading import GraderThresholds, SelfCorrectionConfig
from app.config.models.observability import ObservabilityConfig

class AppConfig(BaseModel):
    """Master config - all sub-configs"""
    llm_generation: OllamaConfig
    llm_grading: GeminiConfig
    embedding: EmbeddingConfig
    postgres: PostgreSQLConfig
    bm25: BM25Config
    retriever: RetrieverConfig
    grader_thresholds: GraderThresholds
    self_correction: SelfCorrectionConfig
    observability: ObservabilityConfig