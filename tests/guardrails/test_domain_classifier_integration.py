# Integration test => Ollama must running

import pytest
from app.guardrails.domain_classifier import classify_domain

@pytest.mark.integration
class TestDomainClassifierRealLLM:

    # In scope
    def test_clearly_in_scope_query(self):
        state = {"user_query": "FastAPI dùng Depends() để làm gì?"}
        result = classify_domain(state)
        assert result["domain_in_scope"] is True

    # Out of scope
    def test_clearly_out_of_scope_query(self):
        state = {"user_query": "Cách nấu phở bò ngon nhất là gì?"}
        result = classify_domain(state)
        assert result["domain_in_scope"] is False
        assert result["final_answer"] is not None