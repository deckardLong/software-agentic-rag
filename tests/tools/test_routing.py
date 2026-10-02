# Test routing

from app.tools.routing import route_after_tool_guardrail, route_after_tool_validation

class TestRouteAfterToolGuardrail:

    def test_allow_routes_to_allow(self):
        """Test allow"""
        assert route_after_tool_guardrail({"tool_guardrail_result": "allow"}) == "allow"

    def test_block_routes_to_block(self):
        """Test block"""
        assert route_after_tool_guardrail({"tool_guardrail_result": "block"}) == "block"


class TestRouteAfterToolValidation:

    def test_valid_routes_to_valid(self):
        """Test valid route"""
        state = {
            "tool_validation_result": "valid"
        }
        assert route_after_tool_validation(state) == "valid"

    def test_invalid_within_retry_limit_routes_to_retry(self):
        """Test invalid route"""
        state = {
            "tool_validation_result": "invalid", 
            "tool_retry_count": 1, 
            "total_retry_count": 1
        }
        assert route_after_tool_validation(state) == "retry"

    def test_invalid_beyond_retry_limit_routes_to_give_up(self):
        """Test invalid to give up (limit retry)"""
        state = {
            "tool_validation_result": "invalid", 
            "tool_retry_count": 10, 
            "total_retry_count": 10
        }
        assert route_after_tool_validation(state) == "give_up"