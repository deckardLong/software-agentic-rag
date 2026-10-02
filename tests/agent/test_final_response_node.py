# Test final resp node

from unittest.mock import patch
from app.agent.nodes.final_response_node import finalize_response, _dedup_sources


class TestDedupSources:

    def test_removes_duplicate_urls(self):
        """Test remove dups"""
        citations = [{
                "type": "document", 
                "url": "https://a.com", 
                "title": "A"
            },
            {
                "type": "document", 
                "url": "https://a.com", 
                "title": "A lại"
            },
            {
                "type": "document", 
                "url": "https://b.com", 
                "title": "B"
            }
        ]
        result = _dedup_sources(citations)
        assert len(result) == 2

    def test_ignores_tool_citations(self):
        """Test ignore tool cites"""
        citations = [{
            "type": "tool", 
            "source": "package_info"
        }]
        assert _dedup_sources(citations) == []


class TestFinalizeResponse:

    @patch("app.agent.nodes.final_response_node.log_query")
    def test_passes_through_valid_answer(self, mock_log):
        """Test valid answer"""
        state = {
            "final_answer": "FastAPI dùng Depends()...", 
            "citations": [], 
            "step_latencies": {}
        }
        result = finalize_response(state)
        assert result["final_answer"] == "FastAPI dùng Depends()..."

    @patch("app.agent.nodes.final_response_node.log_query")
    def test_empty_answer_triggers_safety_net(self, mock_log):
        """Test empty answer"""
        state = {
            "final_answer": "", 
            "citations": [], 
            "step_latencies": {}
        }
        result = finalize_response(state)
        assert "sự cố" in result["final_answer"]

    @patch("app.agent.nodes.final_response_node.log_query")
    def test_calls_log_query_once(self, mock_log):
        """Test calls log query"""
        state = {
            "final_answer": "ok", 
            "citations": [], 
            "step_latencies": {
                "input_guardrail": 5.0
            }
        }
        finalize_response(state)
        mock_log.assert_called_once()

    @patch("app.agent.nodes.final_response_node.log_query", side_effect=Exception("DB down"))
    def test_log_query_failure_does_not_break_response(self, mock_log):
        """Test error log but break response"""
        state = {
            "final_answer": "ok", 
            "citations": [], 
            "step_latencies": {}
        }
        result = finalize_response(state)
        assert result["final_answer"] == "ok"