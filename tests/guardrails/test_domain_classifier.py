# Test node classify_domain

from unittest.mock import MagicMock, patch
from app.guardrails.domain_classifier import classify_domain, _OUT_OF_SCOPE_MESSAGE
from app.guardrails.schemas.domain_classification import DomainClassification

# Mock structured output LLM
def _mock_structured_llm(return_value=None, raise_exception=None):
    """Create mock for LLM structured output"""
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    if raise_exception:
        mock_structured.invoke.side_effect = raise_exception
    else:
        mock_structured.invoke.return_value = return_value
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm

# Test in scope
class TestInScopeQueries:

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_fastapi_query_is_in_scope(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            return_value=DomainClassification(in_scope=True, reason="Câu hỏi về FastAPI")
        )

        state = {"user_query": "FastAPI dùng Depends() để làm gì?"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is True
        assert result["domain_out_of_scope_reason"] is None
        assert "final_answer" not in result  

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_greeting_is_in_scope(self, mock_get_llm):
        """Test greeting (In scope)"""
        mock_get_llm.return_value = _mock_structured_llm(
            return_value=DomainClassification(in_scope=True, reason="Lời chào hợp lệ")
        )

        state = {"user_query": "Xin chào"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is True

# Test out of scope
class TestOutOfScopeQueries:

    # Irrelevant topic
    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_off_topic_query_is_out_of_scope(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            return_value=DomainClassification(in_scope=False, reason="Câu hỏi về nấu ăn, không liên quan software")
        )

        state = {"user_query": "Cách nấu phở bò ngon nhất là gì?"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is False
        assert result["domain_out_of_scope_reason"] == "Câu hỏi về nấu ăn, không liên quan software"
        assert result["final_answer"] == _OUT_OF_SCOPE_MESSAGE


class TestFailOpenBehavior:
    """Test fail-open: LLM crashed => Request still goes on"""

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_llm_connection_error_fails_open(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            raise_exception=ConnectionError("Ollama server unreachable")
        )

        state = {"user_query": "FastAPI dùng Depends() để làm gì?"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is True
        assert result["domain_out_of_scope_reason"] is None
        assert "final_answer" not in result

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_llm_timeout_fails_open(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            raise_exception=TimeoutError("Request timed out")
        )

        state = {"user_query": "Docker container là gì?"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is True

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_llm_schema_validation_error_fails_open(self, mock_get_llm):
        """Mock for case when LLM doesn't return format of DomainClassification schema"""
        from pydantic import ValidationError

        mock_get_llm.return_value = _mock_structured_llm(
            raise_exception=ValidationError.from_exception_data("DomainClassification", [])
        )

        state = {"user_query": "PostgreSQL index hoạt động thế nào?"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is True

# Test when LLM (Ollama) running
class TestObservabilityIntegration:

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_step_latencies_recorded(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            return_value=DomainClassification(in_scope=True, reason="ok")
        )

        state = {"user_query": "Redis pub/sub là gì?"}
        result = classify_domain(state)

        assert "step_latencies" in result
        assert "domain_classifier" in result["step_latencies"]
        assert result["step_latencies"]["domain_classifier"] >= 0

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_step_latencies_preserved_from_previous_node(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            return_value=DomainClassification(in_scope=True, reason="ok")
        )

        state = {
            "user_query": "Redis pub/sub là gì?",
            "step_latencies": {"input_guardrail": 3.2},
        }
        result = classify_domain(state)

        assert "input_guardrail" in result["step_latencies"]
        assert "domain_classifier" in result["step_latencies"]


class TestPromptFormatting:
    """Ensure user query is on format, no wrong format"""

    @patch("app.guardrails.domain_classifier.get_generation_llm")
    def test_query_with_special_characters_does_not_crash(self, mock_get_llm):
        mock_llm = _mock_structured_llm(return_value=DomainClassification(in_scope=True, reason="ok"))
        mock_get_llm.return_value = mock_llm

        # Query has {} 
        state = {"user_query": "Dict trong Python dùng {key: value} như thế nào?"}
        result = classify_domain(state)

        assert result["domain_in_scope"] is True
        # Verify prompt => No empty string
        mock_llm.with_structured_output.return_value.invoke.assert_called_once()
        called_prompt = mock_llm.with_structured_output.return_value.invoke.call_args[0][0]
        assert "Dict trong Python" in called_prompt