# Create embedding model config object

from pydantic import BaseModel

class EmbeddingConfig(BaseModel):
    """Sentence-Transformers embedding configuration"""
    model_name: str = "all-mpnet-base-v2"
    dimension: int = 768
    batch_size: int = 32
    device: str = "cuda"
