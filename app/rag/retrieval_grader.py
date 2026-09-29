# Define retrieval grader node

from pathlib import Path
from app.agent.state import AgentState
from app.config import config
from app.generation.llm_client import get_generation_llm
from app.observability.logger import get_logger
from app.observability.middleware import observe_node
from app.rag.schemas import RetrievalGrade

logger = get_logger(__name__)

_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "generation"
    / "prompt_templates"
    / "retrieval_grader.txt"
)

_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Format docs
def _format_documents(docs: list[dict]) -> str:
    """Format docs for prompt"""
    blocks = []
    for i, doc in enumerate(docs, start=1):
        label = f"{doc.get('source', '')} | {doc.get('heading_path') or doc.get('title', '')}"
        blocks.append(f"[{i}] ({label})\n{doc['content']}")
    return "\n\n".join(blocks)

# Retrieval grade node
@observe_node("retrieval_grader")
def grade_retrieval(state: AgentState) -> dict:
    docs = state.get("reranked_docs", [])
    retry_count = state.get("retrieval_retry_count", 0)
    total_retry_count = state.get("total_retry_count", 0)

    # Irrelevant => Count + 1
    def _irrelevant(annotated_docs: list[dict], score: float) -> dict:
        return {
            "reranked_docs": annotated_docs,
            "retrieval_grade": "irrelevant",
            "retrieval_grade_score": score,
            "retrieval_retry_count": retry_count + 1,
            "total_retry_count": total_retry_count + 1
        }

    if not docs:
        logger.warning(f"Bộ đánh giá chất lượng truy xuất: Không có tài liệu nào để đánh giá")
        return _irrelevant(docs, 0.0)

    # Get prompt
    prompt = _PROMPT_TEMPLATE.format(
        query=state["user_query"],
        search_query=state.get("rewritten_query") or state["user_query"],
        documents=_format_documents(docs)
    )
    structured_llm = get_generation_llm().with_structured_output(RetrievalGrade)

    try:
        result: RetrievalGrade = structured_llm.invoke(prompt)
    except Exception as e:
        logger.error(f"Bộ đánh giá chất lượng truy xuất đã thất bại, lỗi: {e}")
        return {
            "retrieval_grade": "relevant",
            "retrieval_grade_score": 0.0 
        }

    # Relevant
    relevant = {i for i in result.relevant_indices if 1 <= i <= len(docs)}
    annotated = [{**doc, "grader_relevant": (i + 1) in relevant} for i, doc in enumerate(docs)]
    score = round(len(relevant) / len(docs), 4)
    threshold = config.grader_thresholds.retrieval_grade_threshold

    logger.info(f"Bộ đánh giá chất lượng truy xuất: {len(relevant)}/{len(docs)} tài liệu liên quan (score = {score}, threshold = {threshold})")

    # Score >= Threshold
    if score >= threshold:
        return {
            "reranked_docs": annotated,
            "retrieval_grade": "relevant",
            "retrieval_grade_score": score
        }
    return _irrelevant(annotated, score)