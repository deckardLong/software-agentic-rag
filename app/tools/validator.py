# Validation to check format/schema/structure of output from tools

from pydantic import ValidationError
from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.tools.result_schemas import RESULT_SCHEMAS

logger = get_logger(__name__)

# Define validator node
@observe_node("tool_validation")
def validate_tool_result(state: AgentState) -> dict:
    tool_name = state.get("selected_tool")
    raw = state.get("tool_result_raw") or {}
    retry_count = state.get("tool_retry_count", 0)
    total_retry_count = state.get("total_retry_count", 0)

    # Invalid
    def _invalid(reason: str) -> dict:
        return {
            "tool_validation_result": "invalid",
            "tool_validation_error": reason,
            "tool_retry_count": retry_count + 1,
            "total_retry_count": total_retry_count + 1
        }

    if "error" in raw:
        logger.warning(f"Kết quả từ tool không hợp lệ (lỗi thực thi): {raw['error']}")
        return _invalid(raw["error"])

    schema = RESULT_SCHEMAS.get(tool_name)
    if schema is None:
        # database_inspect: not empty dict and not "error"
        if isinstance(raw, dict) and raw:
            return {
                "tool_validation_result": "valid",
                "tool_validation_error": None 
            }
        return _invalid("Kết quả rỗng hoặc không đúng định dạng")

    try:
        schema.model_validate(raw)
    except ValidationError as e:
        logger.warning(f"Kết quả tool không hợp lệ (sai schema) cho '{tool_name}': {e}")
        return _invalid(str(e))

    logger.info(f"Kết quả tool hợp lệ cho '{tool_name}'")
    return {
        "tool_validation_result": "valid",
        "tool_validation_error": None
    }