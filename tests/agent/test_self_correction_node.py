# Test self-correction node

from app.agent.nodes.self_correction_node import self_correct

class TestClassifyByRoute:

    def test_tool_route_targets_tool(self):
        """Test target tool"""
        result = self_correct({
            "route": "tool"
        })
        assert result["self_correction_target"] == "tool"

    def test_direct_route_targets_generation(self):
        """Test target generation"""
        result = self_correct({
            "route": "direct"
        })
        assert result["self_correction_target"] == "generation"


class TestClassifyRagRoute:

    def test_fallback_flag_targets_retrieval(self):
        """Test fallback to retrieval"""
        result = self_correct({
            "route": "rag", 
            "retrieval_fallback": True
        })
        assert result["self_correction_target"] == "retrieval"

    def test_low_retrieval_score_targets_retrieval(self):
        """Test low retrieval score"""
        result = self_correct({
            "route": "rag", 
            "retrieval_grade_score": 0.2
        })
        assert result["self_correction_target"] == "retrieval"

    def test_high_retrieval_score_targets_generation(self):
        """Test hight retrieval score"""
        result = self_correct({
            "route": "rag", 
            "retrieval_grade_score": 0.8
        })
        assert result["self_correction_target"] == "generation"

class TestRetryCounterIncrement:

    def test_retrieval_target_bumps_retrieval_retry_count(self):
        """Test retrieval count increment"""
        result = self_correct({
            "route": "rag", 
            "retrieval_grade_score": 0.1, 
            "retrieval_retry_count": 1
        })
        assert result["retrieval_retry_count"] == 2

    def test_tool_target_bumps_tool_retry_count(self):
        """Test tool count increment"""
        result = self_correct({
            "route": "tool", 
            "tool_retry_count": 0
        })
        assert result["tool_retry_count"] == 1

    def test_generation_target_does_not_add_retry_counters(self):
        """Test generation not add count"""
        result = self_correct({
            "route": "rag", 
            "retrieval_grade_score": 0.9
        })
        assert "retrieval_retry_count" not in result
        assert "tool_retry_count" not in result