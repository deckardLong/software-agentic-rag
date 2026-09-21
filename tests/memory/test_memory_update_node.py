# Test memory update node

from unittest.mock import patch
from app.agent.nodes.memory_update_node import update_memory
from app.memory.long_term_grader import LongTermMemoryGrade

# Test Update Node
class TestMemoryUpdateNode:

    @patch("app.agent.nodes.memory_update_node.grade_for_long_term")
    @patch("app.agent.nodes.memory_update_node.save_long_term_memory")
    @patch("app.agent.nodes.memory_update_node.get_recent_short_term")
    @patch("app.agent.nodes.memory_update_node.save_short_term_turn")
    def test_short_term_always_saved(self, mock_save_short, mock_get_recent, mock_save_long, mock_grade):
        mock_get_recent.return_value = []
        mock_grade.return_value = LongTermMemoryGrade(should_save=False, importance_score=0.2, topic_summary="")

        state = {
            "session_id": "sess-1",
            "trace_id": "trace-1",
            "user_query": "Xin chào",
            "final_answer": "Chào bạn!",
        }
        result = update_memory(state)

        mock_save_short.assert_called_once()
        assert result["should_save_short_term"] is True

    @patch("app.agent.nodes.memory_update_node.grade_for_long_term")
    @patch("app.agent.nodes.memory_update_node.save_long_term_memory")
    @patch("app.agent.nodes.memory_update_node.get_recent_short_term")
    @patch("app.agent.nodes.memory_update_node.save_short_term_turn")
    def test_long_term_saved_when_grader_approves(self, mock_save_short, mock_get_recent, mock_save_long, mock_grade):
        mock_get_recent.return_value = []
        mock_grade.return_value = LongTermMemoryGrade(
            should_save=True, importance_score=0.9, topic_summary="Debug CORS FastAPI"
        )

        state = {
            "session_id": "sess-1",
            "trace_id": "trace-1",
            "user_query": "Sao FastAPI báo lỗi CORS?",
            "final_answer": "Do thiếu middleware...",
        }
        result = update_memory(state)

        mock_save_long.assert_called_once()
        assert result["should_save_long_term"] is True
        assert result["long_term_save_topic"] == "Debug CORS FastAPI"

    @patch("app.agent.nodes.memory_update_node.grade_for_long_term")
    @patch("app.agent.nodes.memory_update_node.save_long_term_memory")
    @patch("app.agent.nodes.memory_update_node.get_recent_short_term")
    @patch("app.agent.nodes.memory_update_node.save_short_term_turn")
    def test_long_term_not_saved_when_grader_rejects(self, mock_save_short, mock_get_recent, mock_save_long, mock_grade):
        mock_get_recent.return_value = []
        mock_grade.return_value = LongTermMemoryGrade(should_save=False, importance_score=0.1, topic_summary="")

        state = {
            "session_id": "sess-1",
            "trace_id": "trace-1",
            "user_query": "Xin chào",
            "final_answer": "Chào bạn!",
        }
        result = update_memory(state)

        mock_save_long.assert_not_called()
        assert result["should_save_long_term"] is False
        assert result["long_term_save_topic"] is None

    def test_no_session_id_skips_update_entirely(self):
        """No MOCK => Bug when session_id is None"""
        state = {"user_query": "Test", "final_answer": "Test answer"}
        result = update_memory(state)

        assert result["should_save_short_term"] is False
        assert result["should_save_long_term"] is False

    @patch("app.agent.nodes.memory_update_node.grade_for_long_term")
    @patch("app.agent.nodes.memory_update_node.save_long_term_memory")
    @patch("app.agent.nodes.memory_update_node.get_recent_short_term")
    @patch("app.agent.nodes.memory_update_node.save_short_term_turn")
    def test_turn_index_increments_correctly(self, mock_save_short, mock_get_recent, mock_save_long, mock_grade):
        """turn_index = turns already have + 1"""
        mock_get_recent.return_value = [{"query": "Q1", "answer": "A1"}, {"query": "Q2", "answer": "A2"}]
        mock_grade.return_value = LongTermMemoryGrade(should_save=False, importance_score=0.1, topic_summary="")

        state = {
            "session_id": "sess-1",
            "trace_id": "trace-1",
            "user_query": "Q3",
            "final_answer": "A3",
        }
        update_memory(state)

        call_kwargs = mock_save_short.call_args
        assert call_kwargs[0][2] == 3  