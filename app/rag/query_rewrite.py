# Handle query rewrite

from pathlib import Path
from app.agent.formatting import format_short_term_context
from app.agent.state import AgentState
from app.generation.llm_client import get_generation_llm
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.rag.schemas import RewrittenQuery

logger = get_logger(__name__)

# Get prompt
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "generation"
    / "prompt_templates"
    / "query_rewrite.txt"
)

_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Build retry hint
def _build_retry_hint(state: AgentState) -> str:
    """Build hint to retry"""
    previous = state.get("rewritten_query")
    if state.get("retrieval_retry_count", 0) > 0 and previous:
        return (
            f'Lần thử trước dùng truy vấn "{previous}" nhưng KHÔNG tìm được tài liệu liên quan. '
            "Hãy diễn đạt khác: từ đồng nghĩa, thuật ngữ chính thức trong tài liệu, hoặc khái niệm rộng hơn.\n"
        )
    return ""

# Define rewrite query node
@observe_node("query_rewrite")
def rewrite_query(state: AgentState) -> dict:
    """"Define query rewrite node"""
    user_query = state["user_query"]
    prompt = _PROMPT_TEMPLATE.format(
        query=user_query,
        short_term_context=format_short_term_context(state.get("short_term_memory", [])),
        retry_hint=_build_retry_hint(state)
    )

    structured_llm = get_generation_llm().with_structured_output(RewrittenQuery)

    try:
        rewritten = structured_llm.invoke(prompt).rewritten_query.strip() or user_query
    except Exception as e:
        logger.error(f"Viết lại câu truy vấn thất bại, sử dụng câu truy vấn gốc: {e}")
        rewritten = user_query

    logger.info(f"Câu truy vấn được viết lại: {user_query!r} -> {rewritten!r}")
    return {
        "rewritten_query": rewritten
    }