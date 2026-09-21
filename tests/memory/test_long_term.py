# Test CRUD long-term memory (MOCK)

from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from app.memory.long_term import save_long_term_memory, search_long_term_memory, _format_vector

# Create MOCK test
def _mock_db_session(mock_session: MagicMock) -> MagicMock:
    mock_cm = MagicMock()
    mock_cm.__enter__ = MagicMock(return_value=mock_session)
    mock_cm.__exit__ = MagicMock(return_value=False)
    return mock_cm

# Test format vector for pgvector
class TestFormatVector:
    def test_formats_as_pgvector_string(self):
        result = _format_vector([0.1, 0.2, 0.3])
        assert result == "[0.1,0.2,0.3]"

    def test_no_spaces_in_output(self):
        result = _format_vector([1.0, 2.0])
        assert " " not in result

# Test save long-term
class TestSaveLongTermMemory:
    @patch("app.memory.long_term.get_db_session")
    @patch("app.memory.long_term.get_embedder")
    def test_embeds_and_saves(self, mock_get_embedder, mock_get_db):
        mock_embedder = MagicMock()
        mock_embedder.embed_query.return_value = [0.1] * 768
        mock_get_embedder.return_value = mock_embedder

        mock_session = MagicMock()
        mock_get_db.return_value = _mock_db_session(mock_session)

        save_long_term_memory(
            session_id="sess-1",
            topic_summary="User đang debug lỗi CORS trong FastAPI",
            importance_score=0.85,
            source_trace_id="trace-1",
        )

        mock_embedder.embed_query.assert_called_once_with("User đang debug lỗi CORS trong FastAPI")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

        saved_row = mock_session.add.call_args[0][0]
        assert saved_row.importance_score == 0.85
        assert saved_row.embedding == [0.1] * 768

# Test search long-term
class TestSearchLongTermMemory:
    @patch("app.memory.long_term.get_db_session")
    @patch("app.memory.long_term.get_embedder")
    def test_filters_by_similarity_threshold(self, mock_get_embedder, mock_get_db):
        """Config default threshold = 0.75 — row below => out."""
        mock_get_embedder.return_value.embed_query.return_value = [0.1] * 768

        rows = [
            SimpleNamespace(id=1, topic_summary="CORS trong FastAPI", importance_score=0.8,
                             created_at=MagicMock(isoformat=lambda: "2026-01-01T00:00:00"), similarity=0.9),
            SimpleNamespace(id=2, topic_summary="Không liên quan lắm", importance_score=0.5,
                             created_at=MagicMock(isoformat=lambda: "2026-01-01T00:00:00"), similarity=0.5),
        ]
        mock_session = MagicMock()
        mock_session.execute.return_value.fetchall.return_value = rows
        mock_get_db.return_value = _mock_db_session(mock_session)

        result = search_long_term_memory("sess-1", "Lỗi CORS là gì?")

        assert len(result) == 1
        assert result[0]["topic"] == "CORS trong FastAPI"
        assert result[0]["similarity"] == 0.9

    @patch("app.memory.long_term.get_db_session")
    @patch("app.memory.long_term.get_embedder")
    def test_returns_empty_when_no_match(self, mock_get_embedder, mock_get_db):
        mock_get_embedder.return_value.embed_query.return_value = [0.1] * 768
        mock_session = MagicMock()
        mock_session.execute.return_value.fetchall.return_value = []
        mock_get_db.return_value = _mock_db_session(mock_session)

        result = search_long_term_memory("sess-empty", "Bất kỳ câu hỏi gì")

        assert result == []