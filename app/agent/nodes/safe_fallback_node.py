# Define safe fallback node 

from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Define patterns
_GROUNDING_EXHAUSTED_MESSAGE = (
    "Mình chưa thể đưa ra câu trả lời đủ chắc chắn cho câu hỏi này dựa trên tài liệu hiện có. "
    "Bạn có thể thử diễn đạt lại câu hỏi cụ thể hơn, hoặc tham khảo trực tiếp các nguồn dưới đây."
)

_OUTPUT_BLOCKED_MESSAGE = (
    "Mình chưa thể cung cấp câu trả lời cho yêu cầu này. Bạn thử diễn đạt lại câu hỏi theo cách khác nhé?"
)

# Format citation links
def _format_citation_links(citations: list[dict]) -> str:
    # Get citations
    doc_citations = [c for c in citations if c.get("type") == "document"]

    # None
    if not doc_citations:
        return ""
    lines = [f"- {c.get('title') or c.get('heading_path') or c['url']}: {c['url']}" for c in doc_citations]
    return "\n\nMột số tài liệu liên quan có thể hữu ích:\n" + "\n".join(lines)

# Define node
@observe_node("safe_fallback")
def safe_fallback_answer(state: AgentState) -> dict:
    if state.get("output_guardrail_result") == "block":
        logger.warning(f"Fallback an toàn: Đã bị chặn tại Output Guardrail")
        return {
            "final_answer": _OUTPUT_BLOCKED_MESSAGE
        }
    logger.warning(f"Fallback an toàn: Đã hết lượt thử lại mức độ bám sát nguồn")
    message = _GROUNDING_EXHAUSTED_MESSAGE + _format_citation_links(state.get("citations", []))
    return {
        "final_answer": message
    }