# Create memory update node

from app.agent.state import AgentState
from app.memory.short_term import save_short_term_turn, get_recent_short_term
from app.memory.long_term import save_long_term_memory
from app.memory.long_term_grader import grade_for_long_term
from app.observability.middleware import observe_node
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Define memory update node
@observe_node("memory_update")
def update_memory(state: AgentState) -> dict:
    session_id = state.get("session_id")

    # If not session_id => Skip
    if not session_id:
        logger.info(f"Không có session_id, bỏ qua bước cập nhật memory")
        return {
            "should_save_short_term": False,
            "should_save_long_term": False
        }
    user_query = state["user_query"]
    final_answer = state.get("final_answer", "")
    trace_id = state["trace_id"]

    # Short-term: Always saved
    existing_turns = get_recent_short_term(session_id)
    turn_index = len(existing_turns) + 1
    save_short_term_turn(session_id, trace_id, turn_index, user_query, final_answer)

    # Long-term: Grader decision
    grade = grade_for_long_term(user_query, final_answer)

    # Should have
    if grade.should_save:
        save_long_term_memory(session_id, grade.topic_summary, grade.importance_score, trace_id)
        logger.info(f"Đã lưu thành công tại long-term memory (importance = {grade.importance_score})")

    # Or not
    else:
        logger.info(f"Không có lưu tại long-term memory")
    return {
        "should_save_short_term": True,
        "should_save_long_term": grade.should_save,
        "long_term_save_topic": grade.topic_summary if grade.should_save else None
    }