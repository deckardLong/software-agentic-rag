# Route after retrieval grade

from app.agent.state import AgentState
from app.config import config

def route_after_retrieval_grade(state: AgentState) -> str:
    if state.get("retrieval_grade") == "relevant":
        return "relevant"

    # Self-correction
    sc = config.self_correction

    can_retry = (
        state.get("retrieval_retry_count", 0) <= sc.max_retrieval_retries
        and state.get("total_retry_count", 0) <= sc.max_total_retries
    )
    return "retry" if can_retry else "fallback"


# After grounding grade
def route_after_grounding_grade(state: AgentState) -> str:
    if state.get("grounding_grade") == "pass":
        return "pass"

    sc = config.self_correction
    can_retry = (
        state.get("generation_retry_count", 0) <= sc.max_generation_retries
        and state.get("total_retry_count", 0) <= sc.max_total_retries
    )    
    return "retry" if can_retry else "safe_fallback"