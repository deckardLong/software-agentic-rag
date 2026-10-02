# Define answer generation node

from pathlib import Path
from langchain_core.messages import HumanMessage
from app.agent.state import AgentState
from app.config import config
from app.generation.llm_client import get_generation_llm
from app.ingestion.token_counter import count_tokens
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Get prompt path
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "generation"
    / "prompt_templates"
    / "answer_generation.txt"
)

_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Create fallback answer
_FALLBACK_ANSWER = "Xin lỗi, hiện mình không thể tạo câu trả lời do sự cố kỹ thuật. Bạn vui lòng thử lại sau nhé."

# Build retry hint
def _build_retry_hint(state: AgentState) -> str:
    if state.get("generation_retry_count", 0) > 0 and state.get("grounding_grade_reason"):
        return (
            f'\nLẦN TRƯỚC câu trả lời bị đánh giá KHÔNG đạt vì: "{state["grounding_grade_reason"]}". '
            "Hãy sửa lại: chỉ khẳng định điều có trong Ngữ cảnh, trích dẫn đầy đủ, không suy diễn thêm.\n"
        )
    return ""

# Define node
@observe_node("answer_generation")
def generate_answer(state: AgentState) -> dict:
    query = state["user_query"]
    context = state.get("assembled_context", "(không có ngữ cảnh bổ sung)")

    # Get prompt
    prompt = _PROMPT_TEMPLATE.format(query=query, context=context, retry_hint=_build_retry_hint(state))

    try:
        response = get_generation_llm().invoke([HumanMessage(content=prompt)])  # get all prompt as a message to send to LLM
    except Exception as e:
        logger.error(f"Lỗi khi call LLM cho Answer Generation: {e}")
        return {
            "draft_answer": _FALLBACK_ANSWER,
            "generation_model": config.llm_generation.model_name,
            "generation_tokens_in": 0,
            "generation_tokens_out": 0
        }

    # Get draft response
    draft = response.content.strip()

    # Get tokens in and out
    usage = getattr(response, "usage_metadata", None) or {}
    tokens_in = usage.get("input_tokens") or count_tokens(prompt)
    tokens_out = usage.get("output_tokens") or count_tokens(draft)

    logger.info(f"Câu trả lời được tạo ra ({tokens_out} token đầu ra)", extra={
        "tokens_in": tokens_in,
        "tokens_out": tokens_out 
    })

    return {
        "draft_answer": draft,
        "generation_model": config.llm_generation.model_name,
        "generation_tokens_in": tokens_in,
        "generation_tokens_out": tokens_out
    }