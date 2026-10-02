# Test execute tool

from unittest.mock import MagicMock, patch
from app.tools.executor import execute_tool

class TestExecuteTool:

    @patch("app.tools.executor.get_tool_spec")
    def test_successful_execution_returns_result(self, mock_get_spec):
        """Test successfull return result"""
        spec = MagicMock()
        spec.execute.return_value = {
            "name": "fastapi", 
            "version": "0.115.0"
        }
        mock_get_spec.return_value = spec

        state = {
            "selected_tool": "package_info", 
            "tool_params": {
                "package_name": "fastapi"
            }}
        result = execute_tool(state)

        assert result["tool_result_raw"]["name"] == "fastapi"

    @patch("app.tools.executor.get_tool_spec")
    def test_exception_during_execution_is_caught(self, mock_get_spec):
        """Test unexpected crash"""
        spec = MagicMock()
        spec.execute.side_effect = RuntimeError("unexpected crash")
        mock_get_spec.return_value = spec

        state = {
            "selected_tool": "package_info", 
            "tool_params": {
                "package_name": "fastapi"
            }}
        result = execute_tool(state)

        assert "error" in result["tool_result_raw"]

    @patch("app.tools.executor.get_tool_spec", return_value=None)
    def test_missing_tool_spec_returns_error_not_crash(self, mock_get_spec):
        """Test missing tool return error"""
        state = {
            "selected_tool": "da_bi_xoa", 
            "tool_params": {}
        }
        result = execute_tool(state)

        assert "error" in result["tool_result_raw"]