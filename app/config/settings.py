# Setting from .env

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache
from app.config.models import (
    AppConfig,
    OllamaConfig,
    GeminiConfig,
    EmbeddingConfig,
    PostgreSQLConfig,
    BM25Config,
    RetrieverConfig,
    GraderThresholds,
    SelfCorrectionConfig,
    ObservabilityConfig,
)

class Settings(BaseSettings): 
    """Load config from .env"""

    # ====== LLM Model (Ollama - Generation) ======
    ollama_model_name: str = Field(default="llama3.1:latest", alias="OLLAMA_MODEL_NAME")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_temperature: float = Field(default=0.7, alias="OLLAMA_TEMPERATURE")
    ollama_max_tokens: int = Field(default=2048, alias="OLLAMA_MAX_TOKENS")
    ollama_timeout_seconds: int = Field(default=60, alias="OLLAMA_TIMEOUT_SECONDS") 

    # ====== LLM Model (Gemini - Evaluation) ======
    gemini_api_key: str = Field(alias="GEMINI_API_KEY")
    gemini_model_name: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL_NAME")
    gemini_temperature: float = Field(default=0.7, alias="GEMINI_TEMPERATURE")
    gemini_max_tokens: int = Field(default=2048, alias="GEMINI_MAX_TOKENS")
    gemini_timeout_seconds: int = Field(default=30, alias="GEMINI_TIMEOUT_SECONDS")
    gemini_max_retries: int = Field(default=3, alias="GEMINI_MAX_RETRIES")

    # ====== Embedding ======
    embedding_model_name: str = Field(default="all-mpnet-base-v2", alias="EMBEDDING_MODEL_NAME")
    embedding_dimension: int = Field(default=768, alias="EMBEDDING_DIMENSION")
    embedding_batch_size: int = Field(default=32, alias="EMBEDDING_BATCH_SIZE")
    embedding_device: str = Field(default="cuda", alias="EMBEDDING_DEVICE")

    # ====== PostgreSQL ======
    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_database: str = Field(default="agentic_rag_db", alias="POSTGRES_DATABASE")
    postgres_user: str = Field(default="postgres", alias="POSTGRES_USER")
    postgres_password: str = Field(default="POSTGRES_PASSWORD")
    postgres_pool_size: int = Field(default=5, alias="POSTGRES_POOL_SIZE")

    # ====== BM25 ======
    bm25_k1: float = Field(default=1.5, alias="BM25_K1")
    bm25_b: float = Field(default=0.75, alias="BM25_B")

    # ====== Retriever ======
    retriever_top_k: int = Field(default=10, alias="RETRIEVER_TOP_K")
    retriever_rerank_top_n: int = Field(default=5, alias="RETRIEVER_RERANK_TOP_N")
    retriever_bm25_weight: float = Field(default=0.3, alias="RETRIEVER_BM25_WEIGHT")
    retriever_vector_weight: float = Field(default=0.7, alias="RETRIEVER_VECTOR_WEIGHT")

    # ====== Thresholds ======
    retrieval_grade_threshold: float = Field(default=0.6, alias="RETRIEVAL_GRADE_THRESHOLD")
    grounding_grade_threshold: float = Field(default=0.7, alias="GROUNDING_GRADE_THRESHOLD")
    long_term_memory_threshold: float = Field(default=0.8, alias="LONG_TERM_MEMORY_THRESHOLD")

    # ====== Self-Correction ======
    max_retrieval_retries: int = Field(default=3, alias="MAX_RETRIEVAL_RETRIES")
    max_generation_retries: int = Field(default=3, alias="MAX_GENERATION_RETRIES")
    max_total_retries: int = Field(default=5, alias="MAX_TOTAL_RETRIES")

    # ====== Observability ======
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", alias="LOG_FILE")
    trace_enabled: bool = Field(default=True, alias="TRACE_ENABLED")
    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    # Build app config
    def build_app_config(self) -> AppConfig:
        """Combine all fields into AppConfig object"""
        return AppConfig(
            llm_generation=OllamaConfig(
                model_name=self.ollama_model_name,
                base_url=self.ollama_base_url,
                temperature=self.ollama_temperature,
                max_tokens=self.ollama_max_tokens,
                timeout_seconds=self.ollama_timeout_seconds,
            ),
            llm_grading=GeminiConfig(
                model_name=self.gemini_model_name,
                api_key=self.gemini_api_key,
                temperature=self.gemini_temperature,
                max_tokens=self.gemini_max_tokens,
                timeout_seconds=self.gemini_timeout_seconds,
                max_retries=self.gemini_max_retries,
            ),
            embedding=EmbeddingConfig(
                model_name=self.embedding_model_name,
                dimension=self.embedding_dimension,
                batch_size=self.embedding_batch_size,
                device=self.embedding_device,
            ),
            postgres=PostgreSQLConfig(
                host=self.postgres_host,
                port=self.postgres_port,
                database=self.postgres_database,
                user=self.postgres_user,
                password=self.postgres_password,
                pool_size=self.postgres_pool_size,
            ),
            bm25=BM25Config(
                k1=self.bm25_k1,
                b=self.bm25_b,
            ),
            retriever=RetrieverConfig(
                top_k=self.retriever_top_k,
                rerank_top_n=self.retriever_rerank_top_n,
                bm25_weight=self.retriever_bm25_weight,
                vector_weight=self.retriever_vector_weight,
            ),
            grader_thresholds=GraderThresholds(
                retrieval_grade_threshold=self.retrieval_grade_threshold,
                grounding_grade_threshold=self.grounding_grade_threshold,
                long_term_memory_threshold=self.long_term_memory_threshold,
            ),
            self_correction=SelfCorrectionConfig(
                max_retrieval_retries=self.max_retrieval_retries,
                max_generation_retries=self.max_generation_retries,
                max_total_retries=self.max_total_retries,
            ),
            observability=ObservabilityConfig(
                log_level=self.log_level,
                log_file=self.log_file,
                trace_enabled=self.trace_enabled,
                metrics_enabled=self.metrics_enabled,
            )
        )

# Get settings
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from .env, cache"""
    return Settings()

# Get app config
@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    """Load app config, cache"""
    return get_settings().build_app_config()