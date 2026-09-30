# Route after tool guardrail & validation

from app.agent.state import AgentState
from app.config import config

# After guardrail
def route_after_tool_guardrail(state: AgentState) -> str:
    return "allow" if state.get("tool_guardrail_result") == "allow" else "block"

# After validation
def route_after_tool_validation(state: AgentState) -> str:
    if state.get("tool_validation_result") == "valid":
        return "valid"

    sc = config.self_correction
    can_retry = (
        state.get("tool_retry_count", 0) <= sc.max_tool_retries
        and state.get("total_retry_count", 0) <= sc.max_total_retries
    )
    return "retry" if can_retry else "give_up"