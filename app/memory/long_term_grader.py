# Grade score for long term memory

from pathlib import Path
from pydantic import BaseModel, Field
from app.generation.llm_client import get_generation_llm
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Define class
class LongTermMemoryGrade(BaseModel):
    should_save: bool = Field(description="True nếu lượt hỏi-đáp này đáng lưu dài hạn")
    importance_score: float = Field(description="Điểm quan trọng 0.0-1.0", ge=0.0, le=1.0)
    topic_summary: str = Field(description="Tóm tắt ngắn gọn chủ đề, dùng để semantic search sau này")

# Get prompt template
_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent
    / "generation"
    / "prompt_templates"
    / "long_term_grader.txt"
)

_PROMPT_TEMPLATE = _PROMPT_PATH.read_text(encoding="utf-8")

# Grade for long term
def grade_for_long_term(user_query: str, final_answer: str) -> LongTermMemoryGrade:
    """Grade for long term memory"""
    prompt = _PROMPT_TEMPLATE.format(query=user_query, answer=final_answer[:1000])
    structured_llm = get_generation_llm().with_structured_output(LongTermMemoryGrade)

    try:
        return structured_llm.invoke(prompt)
    except Exception as e:
        logger.error(f"Lỗi khi call LLM cho Long-Term Grader, mặc định should_have = False: {e}")
        return LongTermMemoryGrade(should_save=False, importance_score=0.0, topic_summary="")