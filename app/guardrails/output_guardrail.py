# Define output guardrail node

import re
from app.agent.state import AgentState
from app.guardrails.patterns.injection_patterns import matches_injection_pattern
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Define patterns
_SECRET_PATTERN = re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\s*[:=]\s*\S+")
_CITATION_PATTERN = re.compile(r"\[(\d+)\]")

# Check non empty
def _check_non_empty(answer: str) -> str | None:
    return "empty_answer" if not answer.strip() else None

# Check leaked secrets
def _check_leaked_secrets(answer: str) -> str | None:
    return "answer_contains_secret_like_pattern" if _SECRET_PATTERN.search(answer) else None

# Check injection echo
def _check_injection_echo(answer: str) -> str | None:
    is_injection, pattern = matches_injection_pattern(answer)
    return f"answer_echoes_injection_pattern: {pattern}" if is_injection else None

# Check citations if it's not in context
def _check_citation_integrity(answer: str, citations: list[dict]) -> str | None:
    cited = {
        int(m) for m in _CITATION_PATTERN.findall(answer)
    }
    if not cited:
        return None
    valid = {
        c["index"] for c in citations if c.get("type") == "document"
    }
    invalid = cited - valid
    return f"citation_index_out_of_range: {sorted(invalid)}" if invalid else None

# Define node
@observe_node("output_guardrail")
def check_output(state: AgentState) -> dict:
    answer = state.get("draft_answer", "")
    citations = state.get("citations", [])

    # Checks
    checks = [
        _check_non_empty(answer),
        _check_leaked_secrets(answer),
        _check_injection_echo(answer),
        _check_citation_integrity(answer, citations)
    ]
    block_reason = next((r for r in checks if r), None)

    # If block reason
    if block_reason:
        logger.warning(f"Đã chặn tại Output Guardrail: {block_reason}")
        return {
            "output_guardrail_result": "block",
            "output_guardrail_block_reason": block_reason
        }
    logger.info("Đã pass qua Output Guardrail")
    return {
        "output_guardrail_result": "pass",
        "output_guardrail_block_reason": None,
        "final_answer": answer
    }