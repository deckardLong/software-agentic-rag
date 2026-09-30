# Handle tool execute

from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.tools.registry import get_tool_spec

logger = get_logger(__name__)

# Define executor node
@observe_node("tool_execution")
def execute_tool(state: AgentState) -> dict:
    """Tool execution node"""
    tool_name = state["selected_tool"]
    params = state.get("tool_params") or {}
    spec = get_tool_spec(tool_name)

    # Spec is None
    if spec is None:
        return {
            "tool_result_raw": {
                "error": f"Tool '{tool_name}' không tồn tại"
            }
        }

    try:
        result = spec.execute(**params)
    except Exception as e:
        logger.error(f"Tool '{tool_name}' thực thi lỗi: {e}")
        result = {
            "error": f"Lỗi khi thực thi tool: {e}"
        }
    logger.info(f"Tool '{tool_name}' đã thực thi", extra={
        "tool": tool_name, 
        "has_error": "error" in result  # to check if error in result (False if it's not )
    })
    return {
        "tool_result_raw": result
    }