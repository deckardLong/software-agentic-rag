# Test database inspect

from unittest.mock import MagicMock, patch
from app.tools.implementations.database_inspect import inspect_database

def _mock_inspector(tables, columns=None):
    # Test mock inspector
    inspector = MagicMock()
    inspector.get_table_names.return_value = tables
    if columns is not None:
        inspector.get_columns.return_value = columns
    return inspector

class TestListTables:

    @patch("app.tools.implementations.database_inspect.inspect")
    def test_returns_table_list(self, mock_inspect):
        """Test return table list"""
        mock_inspect.return_value = _mock_inspector(["documents", "chunks"])

        result = inspect_database("list_tables")

        assert result["tables"] == ["documents", "chunks"]


class TestDescribeTable:

    @patch("app.tools.implementations.database_inspect.inspect")
    def test_unknown_table_rejected(self, mock_inspect):
        """Test unknown table rejected"""
        mock_inspect.return_value = _mock_inspector(["documents"])

        result = inspect_database("describe_table", table_name="ban_khong_ton_tai")

        assert "error" in result

    @patch("app.tools.implementations.database_inspect.inspect")
    def test_valid_table_returns_columns(self, mock_inspect):
        """Test valid table returns cols"""
        mock_inspect.return_value = _mock_inspector(
            ["chunks"], columns=[{"name": "id", "type": "INTEGER"}, {"name": "content", "type": "TEXT"}]
        )

        result = inspect_database("describe_table", table_name="chunks")

        assert result["table"] == "chunks"
        assert len(result["columns"]) == 2


class TestMissingTableName:

    @patch("app.tools.implementations.database_inspect.inspect")
    def test_row_count_requires_table_name(self, mock_inspect):
        """Test missing table"""
        mock_inspect.return_value = _mock_inspector(["chunks"])

        result = inspect_database("row_count", table_name=None)

        assert "error" in result