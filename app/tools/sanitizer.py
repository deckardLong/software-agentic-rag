# Sanitizer for filtering data before context assembly

import re
from app.agent.state import AgentState
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Max string length
MAX_STRING_LENGTH = 2000

# Secret pattern (Ex: Third API returns token/secret)
_SECRET_PATTERN = re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*\S+")
_SECRET_KEY_PATTERN = re.compile(r"(?i)(api[_-]?key|token|secret|password)")

# Sanitize value
def _sanitize_value(value):
    if isinstance(value, str):
        redacted = _SECRET_PATTERN.sub(lambda m: f"{m.group(1)} = [REDACTED]", value)   # hide secret data
        if len(redacted) > MAX_STRING_LENGTH:
            return redacted[:MAX_STRING_LENGTH] + "...(đã cắt bớt)"
        return redacted
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if isinstance(key, str) and _SECRET_KEY_PATTERN.search(key) else _sanitize_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    return value

# Define sanitizer node
@observe_node("tool_sanitization")
def sanitize_tool_result(state: AgentState) -> dict:
    sanitized = _sanitize_value(state.get("tool_result_raw") or {})
    logger.info(f"Kết quả tool đã được lọc cho '{state.get('selected_tool')}'")
    return {
        "sanitized_tool_result": sanitized
    }