# Define direct answer node

from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node


logger = get_logger(__name__)

# Direct answer node
@observe_node("direct_answer")
def skip_retrieval_and_tool(state: AgentState) -> dict:
    logger.info(f"Direct answer route: Bỏ qua Retrieval và Tool")
    return {
        "reranked_docs": [],
        "sanitized_tool_result": None
    }