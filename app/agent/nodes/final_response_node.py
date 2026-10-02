# Define final response node

from app.agent.state import AgentState
from app.db.query_log import log_query
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Empty answer safety net
_EMPTY_ANSWER_SAFETY_NET = "Xin lỗi, đã có sự cố khi tạo câu trả lời. Bạn vui lòng thử lại câu hỏi nhé."

# Dedup sources
def _dedup_sources(citations: list[dict]) -> list[dict]:
    seen_urls: set[str] = set()
    sources = []

    # Traverse each cite
    for c in citations:
        if c.get("type") != "document":
            continue
        url = c.get("url")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        sources.append({
            "title": c.get("title") or c.get("heading_path") or url, 
            "url": url
        })
    return sources

# Define node
@observe_node("final_response")
def finalize_response(state: AgentState) -> dict:
    # Get final answer
    final_answer = state.get("final_answer", "").strip()
    if not final_answer:
        logger.error("final_answer rỗng khi tới Final Response — dùng fallback khẩn cấp")
        final_answer = _EMPTY_ANSWER_SAFETY_NET

    # Sources
    sources = _dedup_sources(state.get("citations", []))

    # Latency
    total_latency = sum(state.get("step_latencies", {}).values())

    logger.info(
        f"Request hoàn tất: {total_latency:.1f}ms tổng, "
        f"retrieval_retry = {state.get('retrieval_retry_count', 0)}, "
        f"generation_retry = {state.get('generation_retry_count', 0)}, "
        f"tool_retry = {state.get('tool_retry_count', 0)}",
        extra={
            "total_latency_ms": round(total_latency, 1)
        }
    )
    try:
        log_query({
            **state,
            "final_answer": final_answer
        }, total_latency)
    except Exception:
        logger.exception("Không thể ghi log truy vấn; vẫn trả response cho người dùng")

    return {
        "final_answer": final_answer,
        "response_sources": sources
    }
