# Test memory retrieval node
from unittest.mock import patch
from app.agent.nodes.memory_retrieval_node import retrieve_memory

class TestMemoryRetrievalNode:

    @patch("app.agent.nodes.memory_retrieval_node.search_long_term_memory")
    @patch("app.agent.nodes.memory_retrieval_node.get_recent_short_term")
    def test_retrieves_both_short_and_long_term(self, mock_short, mock_long):
        mock_short.return_value = [{"query": "Q1", "answer": "A1", "timestamp": "2026-01-01"}]
        mock_long.return_value = [{"topic": "CORS", "summary": "...", "similarity": 0.9}]

        state = {"session_id": "sess-1", "user_query": "FastAPI middleware là gì?"}
        result = retrieve_memory(state)

        assert len(result["short_term_memory"]) == 1
        assert len(result["long_term_memory"]) == 1
        mock_short.assert_called_once_with("sess-1")
        mock_long.assert_called_once_with("sess-1", "FastAPI middleware là gì?")

    def test_no_session_id_skips_memory_entirely(self):
        """No MOCK => Bug when DB doesn't have session_id"""
        state = {"user_query": "Câu hỏi độc lập, không có session"}
        result = retrieve_memory(state)

        assert result["short_term_memory"] == []
        assert result["long_term_memory"] == []

    @patch("app.agent.nodes.memory_retrieval_node.search_long_term_memory")
    @patch("app.agent.nodes.memory_retrieval_node.get_recent_short_term")
    def test_step_latencies_recorded(self, mock_short, mock_long):
        mock_short.return_value = []
        mock_long.return_value = []

        state = {"session_id": "sess-1", "user_query": "Test"}
        result = retrieve_memory(state)

        assert "memory_retrieval" in result["step_latencies"]