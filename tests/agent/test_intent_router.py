# Test intent router node

from unittest.mock import MagicMock, patch
from app.agent.intent_router import route_intent, _format_short_term_context, _format_long_term_context
from app.agent.schemas import IntentRouting

# Create MOCK LLM
def _mock_structured_llm(return_value=None, raise_exception=None):
    mock_llm = MagicMock()
    mock_structured = MagicMock()
    if raise_exception:
        mock_structured.invoke.side_effect = raise_exception
    else:
        mock_structured.invoke.return_value = return_value
    mock_llm.with_structured_output.return_value = mock_structured
    return mock_llm

# Test route to RAG
class TestRouteToRag:
    @patch("app.agent.intent_router.get_generation_llm")
    def test_technical_question_routes_to_rag(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            IntentRouting(route="rag", confidence=0.95, reasoning="Cần tra cứu docs FastAPI")
        )

        state = {"user_query": "FastAPI dùng Depends() để làm gì?", "short_term_memory": [], "long_term_memory": []}
        result = route_intent(state)

        assert result["route"] == "rag"
        assert result["route_confidence"] == 0.95

# Test route to tool
class TestRouteToTool:
    @patch("app.agent.intent_router.get_generation_llm")
    def test_action_request_routes_to_tool(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            IntentRouting(route="tool", confidence=0.88, reasoning="Cần chạy SQL query thực tế")
        )

        state = {"user_query": "Chạy giúp tôi SELECT * FROM users LIMIT 5", "short_term_memory": [], "long_term_memory": []}
        result = route_intent(state)

        assert result["route"] == "tool"

# Test route to direct answer
class TestRouteToDirect:
    @patch("app.agent.intent_router.get_generation_llm")
    def test_greeting_routes_to_direct(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            IntentRouting(route="direct", confidence=0.99, reasoning="Chỉ là lời chào")
        )

        state = {"user_query": "Xin chào", "short_term_memory": [], "long_term_memory": []}
        result = route_intent(state)

        assert result["route"] == "direct"

# Test LLM crashed
class TestFailOpenBehavior:

    @patch("app.agent.intent_router.get_generation_llm")
    def test_llm_error_defaults_to_rag(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(raise_exception=ConnectionError("Ollama down"))

        state = {"user_query": "Bất kỳ câu hỏi gì", "short_term_memory": [], "long_term_memory": []}
        result = route_intent(state)

        assert result["route"] == "rag"
        assert result["route_confidence"] == 0.0

# Test LLM memory format
class TestMemoryContextFormatting:

    def test_empty_short_term_returns_placeholder(self):
        assert _format_short_term_context([]) == "(không có)"

    def test_short_term_formatted_correctly(self):
        memory = [{"query": "FastAPI là gì?", "answer": "FastAPI là một web framework hiện đại cho Python..."}]
        result = _format_short_term_context(memory)
        assert "FastAPI là gì?" in result

    def test_empty_long_term_returns_placeholder(self):
        assert _format_long_term_context([]) == "(không có)"

    def test_long_term_formatted_correctly(self):
        memory = [{"topic": "Debug CORS FastAPI", "similarity": 0.87}]
        result = _format_long_term_context(memory)
        assert "Debug CORS FastAPI" in result
        assert "0.87" in result

    @patch("app.agent.intent_router.get_generation_llm")
    def test_memory_context_injected_into_prompt(self, mock_get_llm):
        """Verify memory actually feed to prompt to LLM, no missing."""
        mock_llm = _mock_structured_llm(IntentRouting(route="rag", confidence=0.9, reasoning="ok"))
        mock_get_llm.return_value = mock_llm

        state = {
            "user_query": "Vậy còn cách xử lý khác thì sao?",
            "short_term_memory": [{"query": "Lỗi CORS là gì?", "answer": "CORS là cơ chế bảo mật..."}],
            "long_term_memory": [],
        }
        route_intent(state)

        called_prompt = mock_llm.with_structured_output.return_value.invoke.call_args[0][0]
        assert "Lỗi CORS là gì?" in called_prompt

# Test node log latencies
class TestObservabilityIntegration:

    @patch("app.agent.intent_router.get_generation_llm")
    def test_step_latencies_recorded(self, mock_get_llm):
        mock_get_llm.return_value = _mock_structured_llm(
            IntentRouting(route="rag", confidence=0.9, reasoning="ok")
        )

        state = {"user_query": "Test", "short_term_memory": [], "long_term_memory": []}
        result = route_intent(state)

        assert "intent_router" in result["step_latencies"]