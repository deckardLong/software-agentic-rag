# Test validate tool

from app.tools.validator import validate_tool_result

class TestValidationSuccess:

    def test_valid_package_info_result(self):
        """Test valid package"""
        state = {
            "selected_tool": "package_info",
            "tool_result_raw": {
                "name": "fastapi", 
                "version": "0.115.0", 
                "summary": "x", 
                "home_page": "y"
            },
        }
        result = validate_tool_result(state)
        assert result["tool_validation_result"] == "valid"

    def test_database_inspect_has_no_fixed_schema(self):
        """Test database inspect"""
        state = {
            "selected_tool": "database_inspect", 
            "tool_result_raw": {
                "tables": ["chunks"]
            }}
        result = validate_tool_result(state)
        assert result["tool_validation_result"] == "valid"

class TestValidationFailure:

    def test_tool_error_marks_invalid(self):
        """Test invalid result"""
        state = {
            "selected_tool": "package_info", 
            "tool_result_raw": {
                "error": "not found"
            }}
        result = validate_tool_result(state)
        assert result["tool_validation_result"] == "invalid"

    def test_schema_mismatch_marks_invalid(self):
        """Test mismatch marks"""
        state = {
            "selected_tool": "package_info",
            "tool_result_raw": {
                "unexpected_field": 123
            },  
        }
        result = validate_tool_result(state)
        assert result["tool_validation_result"] == "invalid"

    def test_empty_database_inspect_result_invalid(self):
        """Test empty database inspect"""
        state = {
            "selected_tool": "database_inspect", 
            "tool_result_raw": {}
        }
        result = validate_tool_result(state)
        assert result["tool_validation_result"] == "invalid"


class TestRetryCounting:

    def test_increments_both_tool_and_total_retry_count(self):
        """Test increment tool and retry count"""
        state = {
            "selected_tool": "package_info",
            "tool_result_raw": {
                "error": "fail"
            },
            "tool_retry_count": 1,
            "total_retry_count": 2,
        }
        result = validate_tool_result(state)
        assert result["tool_retry_count"] == 2
        assert result["total_retry_count"] == 3