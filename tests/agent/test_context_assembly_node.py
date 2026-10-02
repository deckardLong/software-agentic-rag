# Test assembly node

from app.agent.nodes.context_assembly_node import assemble_context, _dedup_docs, _select_docs_within_budget


class TestDedupDocs:

    def test_removes_duplicate_chunk_ids(self):
        """Test remove dups"""
        docs = [{
                "chunk_id": 1, 
                "content": "a"
            }, 
            {
                "chunk_id": 1, 
                "content": "a"
            }, 
            {
                "chunk_id": 2, 
                "content": "b"
            }]
        result = _dedup_docs(docs)
        assert len(result) == 2

    def test_preserves_order(self):
        """Test in order"""
        docs = [{
                "chunk_id": 3, 
                "content": "c"
            }, 
            {
                "chunk_id": 1, 
                "content": "a"
            }]
        result = _dedup_docs(docs)
        assert [d["chunk_id"] for d in result] == [3, 1]


class TestSelectDocsWithinBudget:

    def test_stops_before_exceeding_budget(self):
        """Test stop before exceed"""
        docs = [{
                "content": "word " * 200
            } for _ in range(5)]
        result = _select_docs_within_budget(docs, max_tokens=50)
        assert len(result) < 5

    def test_always_keeps_at_least_one_doc_even_if_it_alone_exceeds_budget(self):
        """Test always keep 1 docs even if it exceeds"""
        docs = [{
            "content": "word " * 500
        }]
        result = _select_docs_within_budget(docs, max_tokens=10)
        assert len(result) == 1


class TestAssembleContextRagOnly:

    def test_includes_rag_section_and_citations(self):
        "Test include rag section + citations"
        state = {
            "reranked_docs": [
                {
                    "chunk_id": 1, 
                    "content": "FastAPI dùng Depends() cho DI", 
                    "source": "fastapi",
                    "url": "https://fastapi.tiangolo.com/tutorial/dependencies/",
                    "heading_path": "Dependencies", 
                    "title": "Dependencies", 
                    "grader_relevant": True
                },
                {
                    "chunk_id": 2, 
                    "content": "Không liên quan", 
                    "source": "fastapi",
                    "url": "https://example.com", 
                    "heading_path": "", 
                    "title": "", 
                    "grader_relevant": False
                },
            ],
            "short_term_memory": [], "long_term_memory": [],
        }
        result = assemble_context(state)

        assert "Tài liệu tham khảo" in result["assembled_context"]
        assert "FastAPI dùng Depends()" in result["assembled_context"]
        assert "Không liên quan" not in result["assembled_context"]  
        assert len(result["citations"]) == 1
        assert result["citations"][0]["type"] == "document"


class TestAssembleContextToolOnly:

    def test_includes_tool_section_and_citation(self):
        """Test include tool section + citations"""
        state = {
            "selected_tool": "package_info",
            "sanitized_tool_result": {
                "name": "fastapi", 
                "version": "0.115.0"
            },
            "short_term_memory": [], 
            "long_term_memory": [],
        }
        result = assemble_context(state)

        assert "Kết quả công cụ: package_info" in result["assembled_context"]
        assert result["citations"] == [{"type": "tool", "source": "package_info"}]


class TestAssembleContextDirect:

    def test_empty_context_when_nothing_to_assemble(self):
        """Test empty context"""
        state = {
            "short_term_memory": [], 
            "long_term_memory": []
        }
        result = assemble_context(state)

        assert "không có ngữ cảnh bổ sung" in result["assembled_context"]
        assert "trả lời trực tiếp" in result["assembled_context"]
        assert result["citations"] == []


class TestAssembleContextFallback:

    def test_adds_warning_note_when_retrieval_fallback(self):
        """Test general knowledge"""
        state = {
            "retrieval_fallback": True, 
            "short_term_memory": [], 
            "long_term_memory": []
        }
        result = assemble_context(state)

        assert "Lưu ý" in result["assembled_context"]
        assert "kiến thức chung" in result["assembled_context"]


class TestAssembleContextMemory:

    def test_includes_short_and_long_term_memory(self):
        """Test include short + long term memory"""
        state = {
            "short_term_memory": [{
                "query": "FastAPI là gì?", 
                "answer": "Framework..."
            }],
            "long_term_memory": [{
                "topic": "Debug CORS FastAPI"
            }],
        }
        result = assemble_context(state)

        assert "Ngữ cảnh hội thoại" in result["assembled_context"]
        assert "FastAPI là gì?" in result["assembled_context"]
        assert "Debug CORS FastAPI" in result["assembled_context"]


class TestObservability:

    def test_step_latencies_recorded(self):
        """Test observability"""
        state = {
            "short_term_memory": [], 
            "long_term_memory": []
        }
        result = assemble_context(state)
        assert "context_assembly" in result["step_latencies"]