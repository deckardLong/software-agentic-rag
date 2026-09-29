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