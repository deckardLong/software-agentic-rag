# Test long-term grader

from unittest.mock import MagicMock, patch
from app.memory.long_term_grader import grade_for_long_term, LongTermMemoryGrade

# Create MOCK test
def _mock_structured_llm(return_value=None, raise_exception=None):
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    if raise_exception:
        mock_structured.invoke.side_effect = raise_exception
    else:
        mock_structured.invoke.return_value = return_value
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm

# Test Grader
class TestGradeForLongTerm:

    # Important query => Save
    @patch("app.memory.long_term_grader.get_generation_llm")
    def test_important_query_should_save(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            LongTermMemoryGrade(should_save=True, importance_score=0.9, topic_summary="Debug lỗi CORS FastAPI")
        )

        result = grade_for_long_term("Sao FastAPI báo lỗi CORS?", "Do thiếu middleware CORS...")

        assert result.should_save is True
        assert result.importance_score == 0.9
        assert result.topic_summary == "Debug lỗi CORS FastAPI"

    # Greeting => Not save
    @patch("app.memory.long_term_grader.get_generation_llm")
    def test_greeting_should_not_save(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            LongTermMemoryGrade(should_save=False, importance_score=0.1, topic_summary="")
        )

        result = grade_for_long_term("Xin chào", "Chào bạn!")

        assert result.should_save is False

    # LLM crashed => Not saved
    @patch("app.memory.long_term_grader.get_generation_llm")
    def test_llm_error_defaults_to_not_saving(self, mock_get_llm):
        """LLM crashed => Not saved => should_have = False"""
        mock_get_llm.return_value = _mock_structured_llm(raise_exception=ConnectionError("Ollama down"))

        result = grade_for_long_term("Câu hỏi bất kỳ", "Trả lời bất kỳ")

        assert result.should_save is False
        assert result.importance_score == 0.0