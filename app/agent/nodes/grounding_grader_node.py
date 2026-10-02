# Define grounding grader node

from pathlib import Path
from app.agent.state import AgentState
from app.config import config
from app.generation.llm_client import get_generation_llm
from app.generation.schemas import GroundingGrade
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Get prompt
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "generation"
    / "prompt_templates"
    / "grounding_grader.txt"
)

_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

_NO_CONTEXT_PLACEHOLDER = "(không có ngữ cảnh bổ sung)"

# Define node
@observe_node("grounding_grader")
def grade_grounding(state: AgentState) -> dict:
    # Get context
    context = state.get("assembled_context", "")

    # Draft
    draft = state.get("draft_answer", "")

    # Retry count
    retry_count = state.get("generation_retry_count", 0)

    # Total retry count
    total_retry_count = state.get("total_retry_count", 0)

    # No context => Direct answer
    if context.strip().startswith(_NO_CONTEXT_PLACEHOLDER):
        logger.info(f"Bộ đánh giá bám sát nguồn: không có ngữ cảnh, tự động pass (trả lời trực tiếp)")
        return {
            "grounding_grade": "pass",
            "grounding_grade_score": 1.0,
            "grounding_grade_reason": None
        }

    # Prompt
    prompt = _PROMPT_TEMPLATE.format(query=state["user_query"], context=context, answer=draft)
    structured_llm = get_generation_llm().with_structured_output(GroundingGrade)

    try:
        result: GroundingGrade = structured_llm.invoke(prompt)
    except Exception as e:
        logger.error(f"Bộ đánh giá bám sát nguồn thất bại, lỗi: {e}")
        return {
            "grounding_grade": "pass",
            "grounding_grade_score": 0.0,
            "grounding_grade_reason": None
        }

    # Setup threshold
    threshold = config.grader_thresholds.grounding_grade_threshold
    passed = result.is_grounded and result.score >= threshold

    logger.info(f"Bộ đánh giá bám sát nguồn dữ liệu: {'PASS' if passed else 'FAIL'} (score = {result.score}, threshold = {threshold})")

    # Passed
    if passed:
        return {
            "grounding_grade": "pass",
            "grounding_grade_score": result.score,
            "grounding_grade_reason": None
        }
    return {
        "grounding_grade": "fail",
        "grounding_grade_score": result.score,
        "grounding_grade_reason": result.reason,
        "generation_retry_count": retry_count + 1,
        "total_retry_count": total_retry_count + 1
    }