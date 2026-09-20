# Define domain classifier node

from pathlib import Path
from app.agent.state import AgentState
from app.generation.llm_client import get_generation_llm
from app.guardrails.schemas.domain_classification import DomainClassification
from app.observability.middleware import observe_node
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Get dir from root to prompt_templates
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "generation"
    / "prompt_templates"
    / "domain_classifier.txt"
)

# Read template
_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Out of scope message
_OUT_OF_SCOPE_MESSAGE = (
    "Mình là trợ lý chuyên về tài liệu kỹ thuật phần mềm (Python, FastAPI, LangChain, "
    "LangGraph, Docker, Kubernetes, PostgreSQL, Redis, GitHub). Câu hỏi này có vẻ nằm "
    "ngoài phạm vi mình hỗ trợ, bạn thử hỏi về 1 trong các công nghệ trên nhé!"
)

# Define node
@observe_node("domain_classifier")
def classify_domain(state: AgentState) -> dict:
    user_query = state["user_query"]
    prompt = _PROMPT_TEMPLATE.format(query=user_query)

    # Get structured output for DomainClassification class
    structured_llm = get_generation_llm().with_structured_output(DomainClassification)
    try:
        result: DomainClassification = structured_llm.invoke(prompt)    # get result from LLM
    except Exception as e:
        logger.error(f"Lỗi khi call LLM cho Domain Classifier: {e}")
        return {
            "domain_in_scope": True,                                    # if it's in scope but LLM crashed => Request go on
            "domain_out_of_scope_reason": None
        }   

    # In scope
    if result.in_scope:
        logger.info(f"Domain classifier: TRONG PHẠM VI (IN SCOPE)")
        return {
            "domain_in_scope": True,                                    
            "domain_out_of_scope_reason": None
        }
    logger.info(f"Domain classifier: NGOÀI PHẠM VI (OUT OF SCOPE) - {result.reason}")
    return {
        "domain_in_scope": False,                                    
        "domain_out_of_scope_reason": result.reason,
        "final_answer": _OUT_OF_SCOPE_MESSAGE
    }