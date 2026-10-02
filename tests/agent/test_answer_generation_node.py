# Test answer generation node

from unittest.mock import MagicMock, patch
from app.agent.nodes.answer_generation_node import generate_answer

def _mock_response(content: str, usage=None):
    msg = MagicMock()
    msg.content = content
    msg.usage_metadata = usage
    return msg

class TestGenerateAnswer:

    @patch("app.agent.nodes.answer_generation_node.get_generation_llm")
    def test_returns_draft_answer_and_token_counts(self, mock_get_llm):
        """Test returns draft + token counts"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response(
            "FastAPI dùng Depends() để tiêm phụ thuộc [1].", usage={"input_tokens": 120, "output_tokens": 15}
        )
        mock_get_llm.return_value = mock_llm

        state = {"user_query": "FastAPI dùng Depends() để làm gì?", "assembled_context": "## Tài liệu\n[1] ..."}
        result = generate_answer(state)

        assert "Depends()" in result["draft_answer"]
        assert result["generation_tokens_in"] == 120
        assert result["generation_tokens_out"] == 15

    @patch("app.agent.nodes.answer_generation_node.get_generation_llm")
    def test_uses_original_vietnamese_query_not_rewritten(self, mock_get_llm):
        """Test uses original query not written"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response("ok")
        mock_get_llm.return_value = mock_llm

        state = {
            "user_query": "FastAPI dùng Depends() để làm gì?",
            "rewritten_query": "How does FastAPI use Depends()?",
            "assembled_context": "ctx",
        }
        generate_answer(state)

        called_prompt = mock_llm.invoke.call_args[0][0][0].content
        assert "FastAPI dùng Depends() để làm gì?" in called_prompt
        assert "How does FastAPI use Depends()" not in called_prompt

    @patch("app.agent.nodes.answer_generation_node.get_generation_llm")
    def test_llm_error_returns_fallback_answer(self, mock_get_llm):
        """Test LLM error returns fallback answer"""
        mock_get_llm.return_value.invoke.side_effect = ConnectionError("Ollama down")

        state = {
            "user_query": "Bất kỳ câu hỏi gì", 
            "assembled_context": "ctx"
        }
        result = generate_answer(state)

        assert "sự cố kỹ thuật" in result["draft_answer"]
        assert result["generation_tokens_in"] == 0

    @patch("app.agent.nodes.answer_generation_node.get_generation_llm")
    def test_retry_hint_included_when_previous_attempt_failed(self, mock_get_llm):
        """Test retry hint"""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = _mock_response("ok")
        mock_get_llm.return_value = mock_llm

        state = {
            "user_query": "Test",
            "assembled_context": "ctx",
            "generation_retry_count": 1,
            "grounding_grade_reason": "Bịa đặt thông tin không có trong ngữ cảnh",
        }
        generate_answer(state)

        called_prompt = mock_llm.invoke.call_args[0][0][0].content
        assert "Bịa đặt thông tin" in called_prompt