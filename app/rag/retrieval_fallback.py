# Define retrieval fallback node

from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

@observe_node("retrieval_fallback")
def fallback_retrieval(state: AgentState) -> dict:
    """Fallback if it doesn't get enough relevant docs"""
    logger.warning(
        "Phương án dự phòng truy xuất: Không tìm được tài liệu nào liên quan khi retry",
        extra={
            "retrieval_retry_count": state.get("retrieval_retry_count", 0)
        }
    )
    return {
        "retrieval_fallback": True,
        "reranked_docs": []
    }