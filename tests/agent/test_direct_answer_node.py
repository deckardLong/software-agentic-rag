# Test direct answer node

from app.agent.nodes.direct_answer_node import skip_retrieval_and_tool

class TestDirectAnswerNode:

    def test_clears_reranked_docs(self):
        """Test leftover reranked docs"""
        state = {
            "user_query": "Xin chào", 
            "reranked_docs": [{
                "content": "sót lại từ query trước"
            }]
        }
        result = skip_retrieval_and_tool(state)
        assert result["reranked_docs"] == []

    def test_clears_sanitized_tool_result(self):
        """Test leftover sanitized tool result"""
        state = {
            "user_query": "Xin chào", 
            "sanitized_tool_result": {
                "leftover": "data"
            }
        }
        result = skip_retrieval_and_tool(state)
        assert result["sanitized_tool_result"] is None

    def test_records_latency(self):
        """Test latency"""
        state = {
            "user_query": "Xin chào"
        }
        result = skip_retrieval_and_tool(state)
        assert "direct_answer" in result["step_latencies"]