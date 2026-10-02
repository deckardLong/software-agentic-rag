from app.agent.nodes.safe_fallback_node import safe_fallback_answer

class TestGroundingExhaustedPath:

    def test_sets_honest_fallback_message(self):
        """Test fallback message"""
        state = {
            "citations": []
        }
        result = safe_fallback_answer(state)
        assert "chưa thể đưa ra câu trả lời" in result["final_answer"]

    def test_includes_citation_links_when_available(self):
        """Test include cites"""
        state = {
            "citations": [{
                "type": "document", 
                "url": "https://fastapi.tiangolo.com", 
                "title": "Deps"
            }]}
        result = safe_fallback_answer(state)
        assert "https://fastapi.tiangolo.com" in result["final_answer"]


class TestOutputBlockedPath:

    def test_vague_message_does_not_leak_block_reason(self):
        """Test cite out of range"""
        state = {
            "output_guardrail_result": "block", 
            "output_guardrail_block_reason": "citation_index_out_of_range: [5]"
        }
        result = safe_fallback_answer(state)
        assert "citation" not in result["final_answer"].lower()
        assert "5" not in result["final_answer"]