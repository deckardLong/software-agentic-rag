# Define self-correction node

from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Define weak retrieval score
WEAK_RETRIEVAL_SCORE = 0.4

# Classify
def _classify(state: AgentState) -> tuple[str, str]:
    """Classify Retrieval, Tool or Generation"""
    route = state.get("route", "rag")

    # Tool
    if route == "tool":
        return "tool", "Ngữ cảnh lấy từ tool nhưng câu trả lời không bám sát - thử lại tool"

    # RAG
    if route == "rag":
        if state.get("retrieval_fallback"):
            return "retrieval", "Đã fallback do không tìm được tài liệu liên quan - thử truy vấn khác"
        score = state.get("retrieval_grade_score", 0.0)
        if score < WEAK_RETRIEVAL_SCORE:
            return "retrieval", f"Điểm truy vấn thấp ({score}) - thử truy vấn khác"
        return "generation", "Ngữ cảnh RAG đủ tốt nhưng câu trả lời vẫn sai lệch - vấn đề ở generation"

    return "generation", "Route direct-answer không có nguồn khác để thử - chỉ còn cách retry generation"

# Define node
@observe_node("self_correction")
def self_correct(state: AgentState) -> dict:
    target, reason = _classify(state)
    logger.warning(f"Tự điều chỉnh: target = {target} - {reason}")

    # Result
    result = {
        "self_correction_target": target,
        "self_correction_reason": reason
    }

    # Count + 1
    if target == "retrieval":
        result["retrieval_retry_count"] = state.get("retrieval_retry_count", 0) + 1
    elif target == "tool":
        result["tool_retry_count"] = state.get("tool_retry_count", 0) + 1
    return result