# Test tool guardrail

from unittest.mock import MagicMock, patch
from app.tools.tool_guardrail import check_tool
from app.tools.implementations.python_sandbox import PythonSandboxArgs
from app.tools.implementations.database_inspect import DatabaseInspectArgs

def _mock_spec(args_schema):
    spec = MagicMock()
    spec.args_schema = args_schema
    return spec

class TestUnknownTool:

    @patch("app.tools.tool_guardrail.get_tool_spec", return_value=None)
    def test_blocks_unknown_tool(self, mock_get_spec):
        """Test block unknown tool"""
        state = {"selected_tool": "khong_ton_tai", "tool_params": {}}
        result = check_tool(state)

        assert result["tool_guardrail_result"] == "block"


class TestInvalidParams:

    @patch("app.tools.tool_guardrail.get_tool_spec")
    def test_blocks_when_args_schema_validation_fails(self, mock_get_spec):
        """Test block when args is not valid"""
        mock_get_spec.return_value = _mock_spec(PythonSandboxArgs)

        state = {
            "selected_tool": "python_sandbox", 
            "tool_params": {}
        }  
        result = check_tool(state)

        assert result["tool_guardrail_result"] == "block"
        assert "Tham số không hợp lệ" in result["tool_guardrail_block_reason"]


class TestRiskRules:

    @patch("app.tools.tool_guardrail.get_tool_spec")
    def test_blocks_sandbox_code_exceeding_max_length(self, mock_get_spec):
        """Test exceed max length"""
        mock_get_spec.return_value = _mock_spec(PythonSandboxArgs)

        state = {
            "selected_tool": "python_sandbox", 
            "tool_params": {
                "code": "x = 1\n" * 1000
            }
        }
        result = check_tool(state)

        assert result["tool_guardrail_result"] == "block"

    @patch("app.tools.tool_guardrail.get_tool_spec")
    def test_blocks_sample_rows_on_conversation_tables(self, mock_get_spec):
        """Test block sample rows (conversation tables)"""
        mock_get_spec.return_value = _mock_spec(DatabaseInspectArgs)

        state = {
            "selected_tool": "database_inspect",
            "tool_params": {
                "operation": "sample_rows", 
                "table_name": "conversation_short_term"
            },
        }
        result = check_tool(state)

        assert result["tool_guardrail_result"] == "block"

    @patch("app.tools.tool_guardrail.get_tool_spec")
    def test_allows_valid_safe_call(self, mock_get_spec):
        """Test allow valid call"""
        mock_get_spec.return_value = _mock_spec(PythonSandboxArgs)

        state = {
            "selected_tool": "python_sandbox", 
            "tool_params": {
                "code": "print(1)"
            }
        }
        result = check_tool(state)

        assert result["tool_guardrail_result"] == "allow"
        assert result["tool_guardrail_block_reason"] is None