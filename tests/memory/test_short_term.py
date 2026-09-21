# Test CRUD short-term memory (MOCK)

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from app.memory.short_term import (
    save_short_term_turn,
    get_recent_short_term,
    delete_expired_short_term,
)

def _mock_db_session(mock_session: MagicMock) -> MagicMock:
    """Mock `with get_db_session() as session:` — return context manager mock."""
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_session)
    mock_cm.__exit__ = MagicMock(return_value=False)
    return mock_cm

# Test save short term turn
class TestSaveShortTermTurn:
    @patch("app.memory.short_term.get_db_session")
    def test_saves_turn_with_add_and_commit(self, mock_get_db):
        mock_session = MagicMock()
        mock_get_db.return_value = _mock_db_session(mock_session)

        save_short_term_turn(
            session_id="sess-1",
            trace_id="trace-1",
            turn_index=1,
            user_query="FastAPI là gì?",
            final_answer="FastAPI là 1 web framework...",
        )

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        saved_row = mock_session.add.call_args[0][0]
        assert saved_row.session_id == "sess-1"
        assert saved_row.user_query == "FastAPI là gì?"
        assert saved_row.expires_at > datetime.now(timezone.utc)

# Test get recent short term
class TestGetRecentShortTerm:

    @patch("app.memory.short_term.get_db_session")
    def test_returns_turns_in_chronological_order(self, mock_get_db):
        """DB return sequential desc (new first) — func must return asc (old -> new)."""
        now = datetime.now(timezone.utc)
        # Mock DB return desc: turn 2 (new) first, turn 1 (old) after
        rows = [
            SimpleNamespace(user_query="Câu hỏi 2", final_answer="Trả lời 2", created_at=now),
            SimpleNamespace(user_query="Câu hỏi 1", final_answer="Trả lời 1", created_at=now - timedelta(minutes=5)),
        ]
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = rows
        mock_get_db.return_value = _mock_db_session(mock_session)

        result = get_recent_short_term("sess-1")

        assert len(result) == 2
        # After reverse: Q1 (old) must before Q2 (new)
        assert result[0]["query"] == "Câu hỏi 1"
        assert result[1]["query"] == "Câu hỏi 2"

    # Empty turn
    @patch("app.memory.short_term.get_db_session")
    def test_returns_empty_list_when_no_turns(self, mock_get_db):
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_db.return_value = _mock_db_session(mock_session)

        result = get_recent_short_term("sess-empty")

        assert result == []

# Test delete expired short term
class TestDeleteExpiredShortTerm:
    @patch("app.memory.short_term.get_db_session")
    def test_returns_deleted_count(self, mock_get_db):
        mock_session = MagicMock()
        mock_session.execute.return_value.rowcount = 7
        mock_get_db.return_value = _mock_db_session(mock_session)

        deleted = delete_expired_short_term()

        assert deleted == 7
        mock_session.commit.assert_called_once()