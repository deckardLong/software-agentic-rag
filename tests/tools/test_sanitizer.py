# Test sanitize tool

from app.tools.sanitizer import sanitize_tool_result

class TestSecretRedaction:

    def test_redacts_api_key_pattern(self):
        """Test API key pattern"""
        state = {
            "selected_tool": "web_search", 
            "tool_result_raw": {
                "body": "api_key=sk-abc123xyz"
            }}
        result = sanitize_tool_result(state)
        assert "sk-abc123xyz" not in result["sanitized_tool_result"]["body"]
        assert "[REDACTED]" in result["sanitized_tool_result"]["body"]

    def test_redacts_nested_secret(self):
        """Test nested secret"""
        state = {
            "selected_tool": "web_search", 
            "tool_result_raw": {
                "nested": {
                    "token": "secret-value-here"
                    }
                }
            }
        result = sanitize_tool_result(state)
        assert "secret-value-here" not in str(result["sanitized_tool_result"])


class TestLengthTruncation:

    def test_truncates_long_string(self):
        """Test truncate long string"""
        state = {
            "selected_tool": "python_sandbox", 
            "tool_result_raw": {
                "stdout": "a" * 5000
            }}
        result = sanitize_tool_result(state)
        assert len(result["sanitized_tool_result"]["stdout"]) <= 2050  # cap + suffix marker


class TestListHandling:

    def test_sanitizes_each_item_in_list(self):
        """Test sanitizes each item"""
        state = {
            "selected_tool": "github_search", 
            "tool_result_raw": {
                "results": [{
                    "description": "token=abc123"
                    }]
                }
            }
        result = sanitize_tool_result(state)
        assert "[REDACTED]" in result["sanitized_tool_result"]["results"][0]["description"]