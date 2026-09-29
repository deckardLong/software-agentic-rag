# Handle intent router (RAG / Direct Answer / Tools)

from pathlib import Path
from app.agent.state import AgentState
from app.agent.schemas import IntentRouting
from app.generation.llm_client import get_generation_llm
from app.observability.middleware import observe_node
from app.agent.formatting import (
    format_short_term_context as _format_short_term_context,
    format_long_term_context as _format_long_term_context
)
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Get prompt template
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "generation"
    / "prompt_templates"
    / "intent_router.txt"
)
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Define router intent 
@observe_node("intent_router")
def route_intent(state: AgentState) -> dict:
    """Intent Route"""
    user_query = state["user_query"]
    short_term_memory = state.get("short_term_memory", [])
    long_term_memory = state.get("long_term_memory", [])

    # Get prompt
    prompt = _PROMPT_TEMPLATE.format(
        query=user_query,
        short_term_context=_format_short_term_context(short_term_memory),
        long_term_context=_format_long_term_context(long_term_memory)
    )

    structured_llm = get_generation_llm().with_structured_output(IntentRouting)

    try:
        result: IntentRouting = structured_llm.invoke(prompt)
    except Exception as e:
        # Fail-open to RAG, avoid answer being hallucination when LLM crashed (must be based-on docs saved in pgvector)
        logger.error(f"Lỗi khi call LLM tại Intent Router, mặc định 'rag': {e}")
        return {
            "route": "rag",
            "route_confidence": 0.0
        } 

    logger.info(
        f"Điều hướng sang '{result.route}' (confidence = {result.confidence}): {result.reasoning}",
        extra={
            "route": result.route,
            "confidence": result.confidence
        }
    )
    return {
        "route": result.route,
        "route_confidence": result.confidence
    }