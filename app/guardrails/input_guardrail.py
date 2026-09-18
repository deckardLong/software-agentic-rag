# Injection / Manage length / Schema

from app.agent.state import AgentState
from app.guardrails.patterns.injection_patterns import matches_injection_pattern
from app.observability.logger import get_logger
from app.observability.trace_context import new_trace_id
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Setup query length
MIN_QUERY_LENGTH = 3
MAX_QUERY_LENGTH = 2000

# Check schema
def _check_schema(state: AgentState) -> str | None:
    """Check fields whether mandatory or exact data type. Return reason why it's failed or None if it's passed"""
    user_query = state.get("user_query")

    if user_query is None:
        return "missing_user_query"
    if not isinstance(user_query, str):
        return "user_query_not_string"
    if not user_query.strip():
        return "empty_user_query"
    return None

# Check length
def _check_length(user_query: str) -> str | None:
    """Check the length of query, return reason why it's failed or None if it's passed"""
    stripped = user_query.strip()

    if len(stripped) < MIN_QUERY_LENGTH:
        return f"query_too_short (min = {MIN_QUERY_LENGTH})"
    if len(stripped) > MAX_QUERY_LENGTH:
        return f"query_too_long (max = {MAX_QUERY_LENGTH})"
    return None

# Check injection
def _check_injection(user_query: str) -> str | None:
    """Check prompt injection pattern, return why it's failed and matched pattern, or None if it's passed"""
    is_injection, matched_pattern = matches_injection_pattern(user_query)

    if is_injection:
        return f"injection_pattern_matched: {matched_pattern}"
    return None

# Get friendly rejection message
def _friendly_rejection_message(fail_reason: str) -> str:
    """Display info for user => friendly message"""
    if fail_reason.startswith(("missing_user_query", "user_query_not_string", "empty_user_query")):
        return "Mình chưa nhận được câu hỏi nào cả. Bạn nhập lại giúp mình nhé?"

    if fail_reason.startswith("query_too_short"):
        return "Câu hỏi có vẻ hơi ngắn, bạn mô tả rõ hơn một chút để mình hỗ trợ tốt hơn nhé?"

    if fail_reason.startswith("query_too_long"):
        return "Câu hỏi hơi dài, bạn rút gọn lại giúp mình nhé?"

    if fail_reason.startswith("injection_pattern_matched"):
        return "Mình chưa thể xử lý yêu cầu này. Bạn thử diễn đạt lại câu hỏi theo cách khác nhé?"
    return "Xin lỗi, mình chưa thể xử lý yêu cầu này. Bạn thử lại nhé?"

# Check input
@observe_node("input_guardrail")
def check_input(state: AgentState) -> dict:
    """
    Node: Input Guardrail => Initialize trace_id
    """
    trace_id =  new_trace_id()
    user_query = state.get("user_query", "")
    user_query = str(user_query)                                                         # avoid errors if input is numbers

    logger.info(f"Request mới đầu vào: {str(user_query)[:80]!r}")                        # display special characters: "\n", "\t", ...

    # Run 3 checks sequentially
    checks = [
        _check_schema(state),
        _check_length(user_query) if isinstance(user_query, str) else "schema_check_failed_skip_length",
        _check_injection(user_query) if isinstance(user_query, str) else "schema_check_failed_skip_injection"
    ]

    fail_reason = next((reason for reason in checks if reason is not None), None)   # get failed reason
    if fail_reason:
        logger.warning(f"Đã thất bại tại Input Guardrail: {fail_reason}")
        return {
            "trace_id": trace_id,
            "input_guardrail_result": "fail",
            "input_guardrail_reason": fail_reason,
            "final_answer": _friendly_rejection_message(fail_reason)
        }

    logger.info("Đã qua thành công tại Input Guardrail")
    return {
        "trace_id": trace_id,
        "input_guardrail_result": "pass",
        "input_guardrail_reason": None
    }
