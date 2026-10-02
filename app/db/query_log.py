# Write in 1 row in QueryLog

from app.agent.state import AgentState
from app.db import get_db_session
from app.db.models import QueryLog
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Log query
def log_query(state: AgentState, total_latency_ms: float) -> None:
    try:
        with get_db_session() as session:
            session.add(QueryLog(
                trace_id=state["trace_id"],
                session_id=state.get("session_id"),
                user_query=state["user_query"],
                route=state.get("route"),
                final_answer=state.get("final_answer"),
                input_guardrail_result=state.get("input_guardrail_result"),
                output_guardrail_result=state.get("output_guardrail_result"),
                grounding_grade=state.get("grounding_grade"),
                total_retry_count=state.get("total_retry_count", 0),
                latency_ms=round(total_latency_ms),
                llm_tokens_in=state.get("generation_tokens_in"),
                llm_tokens_out=state.get("generation_tokens_out"),
            ))
            session.commit()
    except Exception as e:
        logger.error(f"Không ghi được query_log: {e}")