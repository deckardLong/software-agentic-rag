# Define tool selection node

from pathlib import Path
from app.agent.state import AgentState
from app.generation.llm_client import get_generation_llm
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.tools.registry import list_tool_descriptions, get_tool_spec
from app.tools.schemas import ToolSelection

logger = get_logger(__name__)

# Get prompt path
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "generation"
    / "prompt_templates"
    / "tool_selection.txt"
)

_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Tool selection node
@observe_node("tool_selection")
def select_tool(state: AgentState) -> dict:
    # Get query
    query = state.get("rewritten_query") or state["user_query"]

    # Prompt
    prompt = _PROMPT_TEMPLATE.format(query=query, tool_descriptions=list_tool_descriptions())

    structured_llm = get_generation_llm().with_structured_output(ToolSelection)

    try:
        result: ToolSelection = structured_llm.invoke(prompt)
    except Exception as e:
        logger.error(f"Việc chọn tool thất bại, fallback sang RAG: {e}")
        return {
            "selected_tool": None
        }

    # If tool doesn't exist
    if get_tool_spec(result.tool_name) is None:
        logger.warning(f"LLM chọn tool không tồn tại '{result.tool_name}', fallback sang RAG")
        return {
            "selected_tool": None
        }

    logger.info(f"Tool được chọn: {result.tool_name} ({result.reasoning})")
    return {
        "selected_tool": result.tool_name,
        "tool_params": result.tool_params
    }