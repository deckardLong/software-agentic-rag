# Create memory config object

from pydantic import BaseModel

class MemoryConfig(BaseModel):
    """Define thresholds for long / short term memories"""
    short_term_ttl_hours: int = 24                  # after 24h, memory's gone
    short_term_max_turns: int = 10                  # maximum turn = 10 / session => Avoid keeping context too large
    long_term_top_k: int = 3                        # get 3 most relevant memory
    long_term_similarity_threshold: float = 0.75    # memory relevant if > 0.75