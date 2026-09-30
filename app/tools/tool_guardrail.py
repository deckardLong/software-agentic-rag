# Guardrail to check risk/permission tools

from pydantic import ValidationError
from app.agent.state import AgentState
from app.config import config
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.tools.registry import get_tool_spec

logger = get_logger(__name__)

# Check risk rules
def _check_risk_rules(tool_name: str, params: dict) -> str | None:
    """Reason for BLOCK & None if ALLOW"""
    cfg = config.tool_guardrail

    # Sandbox
    if tool_name == "python_sandbox":
        code = params.get("code", "")
        if len(code) > cfg.sandbox_max_code_length:
            return f"Code vượt quá giới hạn {cfg.sandbox_max_code_length} ký tự"

    # Database inspect
    if tool_name == "database_inspect":
        if params.get("operation") == "sample_rows" and params.get("table_name") in cfg.database_inspect_blocked_tables:
            return f"Bảng '{params.get('table_name')}' chứa dữ liệu hội thoại người dùng, không cho xem dữ liệu mẫu"
    return None

# Define check tool node
@observe_node("tool_guardrail")
def check_tool(state: AgentState) -> dict:
    tool_name = state.get("selected_tool")
    params = state.get("tool_params") or {}
    spec = get_tool_spec(tool_name)

    # None
    if spec is None:
        logger.warning(f"Tool guardrail: tool '{tool_name}' không tồn tại")
        return {
            "tool_guardrail_result": "block",
            "tool_guardrail_block_reason": f"Tool '{tool_name}' không tồn tại"
        }

    try:
        spec.args_schema(**params)
    except ValidationError as e:
        logger.warning(f"Tool guardrail: tham số không hợp lệ cho '{tool_name}': {e}")
        return {
            "tool_guardrail_result": "block",
            "tool_guardrail_block_reason": f"Tham số không hợp lệ: {e}"
        }

    # Risk
    risk_reason = _check_risk_rules(tool_name, params)
    if risk_reason:
        logger.warning(f"Tool guardrail chặn '{tool_name}': {risk_reason}")
        return {
            "tool_guardrail_result": "block",
            "tool_guardrail_block_reason": risk_reason
        }

    logger.info(f"Tool guardrail cho phép: {tool_name}")
    return {
        "tool_guardrail_result": "allow",
        "tool_guardrail_block_reason": None
    }