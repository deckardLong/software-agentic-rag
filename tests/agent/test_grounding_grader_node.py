# Test grounding grader node

from unittest.mock import MagicMock, patch
from app.agent.nodes.grounding_grader_node import grade_grounding
from app.generation.schemas import GroundingGrade

def _mock_structured_llm(return_value=None, raise_exception=None):
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    if raise_exception:
        mock_structured.invoke.side_effect = raise_exception
    else:
        mock_structured.invoke.return_value = return_value
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm


class TestNoContextAutoPass:

    def test_direct_answer_route_skips_llm_call(self):
        """Test direct answer"""
        state = {
            "user_query": "Xin chào",
            "draft_answer": "Chào bạn!",
            "assembled_context": "(không có context bổ sung — trả lời trực tiếp)",
        }
        result = grade_grounding(state)

        assert result["grounding_grade"] == "pass"
        assert result["grounding_grade_score"] == 1.0


class TestGradingWithContext:

    @patch("app.agent.nodes.grounding_grader_node.get_generation_llm")
    def test_grounded_answer_passes(self, mock_get_llm):
        """Test grounded answer"""
        mock_get_llm.return_value = _mock_structured_llm(
            GroundingGrade(is_grounded=True, score=0.9, reason="Khớp tài liệu [1]")
        )

        state = {
            "user_query": "Q", 
            "draft_answer": "A [1]", 
            "assembled_context": "## Tài liệu\n[1] ..."
        }
        result = grade_grounding(state)

        assert result["grounding_grade"] == "pass"
        assert result["grounding_grade_reason"] is None

    @patch("app.agent.nodes.grounding_grader_node.get_generation_llm")
    def test_hallucinated_answer_fails_and_increments_retry(self, mock_get_llm):
        """Test hallucinated answer"""
        mock_get_llm.return_value = _mock_structured_llm(
            GroundingGrade(is_grounded=False, score=0.2, reason="Claim về X không có trong ngữ cảnh")
        )

        state = {
            "user_query": "Q", 
            "draft_answer": "A bịa", 
            "assembled_context": "## Tài liệu\n[1] ...",
            "generation_retry_count": 0, 
            "total_retry_count": 0,
        }
        result = grade_grounding(state)

        assert result["grounding_grade"] == "fail"
        assert result["generation_retry_count"] == 1
        assert result["total_retry_count"] == 1
        assert "không có trong ngữ cảnh" in result["grounding_grade_reason"]

    @patch("app.agent.nodes.grounding_grader_node.get_generation_llm")
    def test_score_below_threshold_fails_even_if_is_grounded_true(self, mock_get_llm):
        """Test score below threshold"""
        mock_get_llm.return_value = _mock_structured_llm(
            GroundingGrade(is_grounded=True, score=0.3, reason="Đúng nhưng mơ hồ")
        )

        state = {
            "user_query": "Q", 
            "draft_answer": "A", 
            "assembled_context": "ctx", 
            "generation_retry_count": 0, 
            "total_retry_count": 0
        }
        result = grade_grounding(state)

        assert result["grounding_grade"] == "fail"


class TestFailOpenBehavior:

    @patch("app.agent.nodes.grounding_grader_node.get_generation_llm")
    def test_llm_error_fails_open_to_pass(self, mock_get_llm):
        """Test LLM error"""
        mock_get_llm.return_value = _mock_structured_llm(raise_exception=ConnectionError("down"))

        state = {
            "user_query": "Q", 
            "draft_answer": "A", 
            "assembled_context": "## ctx"
        }
        result = grade_grounding(state)

        assert result["grounding_grade"] == "pass"
        assert result["grounding_grade_score"] == 0.0