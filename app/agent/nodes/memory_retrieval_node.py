# Create memory retrieval node to retrieve memory before intent router

from app.agent.state import AgentState
from app.memory.short_term import get_recent_short_term
from app.memory.long_term import search_long_term_memory
from app.observability.middleware import observe_node
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Define memory retrieval node
@observe_node("memory_retrieval")
def retrieve_memory(state: AgentState) -> dict:
    """Retrieve memory from pgvector"""
    session_id = state.get("session_id")
    user_query = state["user_query"]

    # Check if request doesn't belong to conversation that saved
    if not session_id:
        # Independent request
        logger.info(f"Không nằm trong session_id nào đã lưu, bỏ qua bước memory retrieval")
        return {
            "short_term_memory": [],
            "long_term_memory": []
        }

    # Get short & long term
    short_term = get_recent_short_term(session_id)
    long_term = search_long_term_memory(session_id, user_query)

    logger.info(
        f"Memory đã truy xuất: {len(short_term)} short-term, {len(long_term)} long-term",
        extra={
            "short_term_count": len(short_term),
            "long_term_count": len(long_term)
        }
    )
    return {
        "short_term_memory": short_term,
        "long_term_memory": long_term
    }