# Test routing grounding

from app.agent.routing import route_after_grounding_grade

class TestRouteAfterGroundingGrade:

    def test_pass_routes_to_pass(self):
        """Test pass routes to pass"""
        assert route_after_grounding_grade({"grounding_grade": "pass"}) == "pass"

    def test_fail_within_retry_limit_routes_to_retry(self):
        """Test fail within retry limit"""
        state = {
            "grounding_grade": "fail", 
            "generation_retry_count": 1, 
            "total_retry_count": 1
        }
        assert route_after_grounding_grade(state) == "retry"

    def test_fail_beyond_retry_limit_routes_to_safe_fallback(self):
        """Test fail to safe fallback"""
        state = {
            "grounding_grade": "fail", 
            "generation_retry_count": 10, 
            "total_retry_count": 10
        }
        assert route_after_grounding_grade(state) == "safe_fallback"

    def test_fail_beyond_limit_routes_to_safe_fallback_string(self):
        """Test fail beyond to safe fallback"""
        state = {
            "grounding_grade": "fail", 
            "generation_retry_count": 99, 
            "total_retry_count": 99
        }
        assert route_after_grounding_grade(state) == "safe_fallback"