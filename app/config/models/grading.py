# Create grading config object

from pydantic import BaseModel

class GraderThresholds(BaseModel):
    """Thresholds for all grader (retrieval, grounding and long-term memory)"""
    retrieval_grade_threshold: float = 0.6
    grounding_grade_threshold: float = 0.7
    long_term_memory_threshold: float = 0.8

class SelfCorrectionConfig(BaseModel):
    """Retry policy"""
    max_retrieval_retries: int = 3
    max_generation_retries: int = 3
    max_total_retries: int = 5