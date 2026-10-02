# Define context assembly node

import json
from app.agent.state import AgentState
from app.config import config
from app.ingestion.token_counter import count_tokens
from app.observability.logger import get_logger
from app.observability.middleware import observe_node

logger = get_logger(__name__)

# Dedup docs
def _dedup_docs(docs: list[dict]) -> list[dict]:
    """Dedup by chunk_id"""
    seen: set[int] = set()
    result = []
    for doc in docs:
        chunk_id = doc.get("chunk_id")
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        result.append(doc)
    return result

# Select docs within budget
def _select_docs_within_budget(docs: list[dict], max_tokens: int) -> list[dict]:
    """If reranked docs overflows the limit of max tokens => Stop"""
    selected, used = [], 0
    for doc in docs:
        doc_tokens = count_tokens(doc["content"])
        if used + doc_tokens > max_tokens and selected:
            break
        selected.append(doc)
        used += doc_tokens
    return selected

# Format RAG section
def _format_rag_section(docs: list[dict]) -> tuple[str, list[dict]]:
    """Format section by each doc"""
    if not docs:
        return "", []
    blocks, citations = [], []
    for i, doc in enumerate(docs, start=1):
        label = doc.get("heading_path") or doc.get("title") or doc["url"]
        blocks.append(f"[{i}] ({doc['source']} | {label})\n{doc['content']}")
        citations.append({
            "type": "document",
            "index": i,
            "source": doc["source"],
            "url": doc["url"],
            "title": doc.get("title"),
            "heading_path": doc.get("heading_path")
        })
    section = "## Tài liệu tham khảo\n\n" + "\n\n".join(blocks)
    return section, citations

# Format tool section
def _format_tool_section(tool_name: str | None, result: dict | None, max_tokens: int) -> tuple[str, list[dict]]:
    """Format structured tool selection"""
    if not result:
        return "", []

    # Get text
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if count_tokens(text) > max_tokens:
        text = text[:max_tokens * 3] + "\n...(đã cắt bớt)"

    # Get section
    section = f"## Kết quả công cụ: {tool_name}\n\n{text}"
    citation = [{
        "type": "tool",
        "source": tool_name
    }]
    return section, citation

# Format memory section
def _format_memory_section(state: AgentState, max_tokens: int) -> str:
    """Format short + long term memory section"""
    # Get short + long term
    short_term = state.get("short_term_memory", [])
    long_term = state.get("long_term_memory", [])

    if not short_term and not long_term:
        return ""

    parts, used = [], 0
    if short_term:
        lines = [f'- Hỏi: "{t["query"]}" | Đáp: "{t["answer"][:150]}..."' for t in short_term]
        block = "### Lịch sử hội thoại gần đây\n" + "\n".join(lines)
        if (t := count_tokens(block)) <= max_tokens:
            parts.append(block)
            used += t

    if long_term:
        lines = [f'- {m["topic"]}' for m in long_term]
        block = "### Chủ đề đã trao đổi trước đó\n" + "\n".join(lines)
        if used + count_tokens(block) <= max_tokens:
            parts.append(block)

    return "## Ngữ cảnh hội thoại\n\n" + "\n\n".join(parts) if parts else ""
    
# Define node
@observe_node("context_assembly")
def assemble_context(state: AgentState) -> dict:
    cfg = config.context_assembly

    # Get raw docs
    raw_docs = _dedup_docs([d for d in state.get("reranked_docs", []) if d.get("grader_relevant")])
    docs = _select_docs_within_budget(raw_docs, cfg.max_rag_tokens)

    # Get RAG section
    rag_section, rag_citations = _format_rag_section(docs)

    # Get tool section
    tool_section, tool_citations = _format_tool_section(
        state.get("selected_tool"), state.get("sanitized_tool_result"), cfg.max_tool_result_tokens
    )

    # Get memory section
    memory_section = _format_memory_section(state, cfg.max_memory_tokens)

    # All sections
    sections = [s for s in (rag_section, tool_section, memory_section) if s]

    # Fallback to user if the retrieval cannot find docs in corpus
    if state.get("retrieval_fallback"):
        sections.insert(0, (
            "## Lưu ý\nKhông tìm được tài liệu liên quan trong kho dữ liệu sau nhiều lần thử. "
            "Câu trả lời dưới đây (nếu có) dựa trên kiến thức chung, KHÔNG có nguồn tham khảo cụ thể — "
            "cần cảnh báo rõ điều này với người dùng."
        ))

    assembled = "\n\n".join(sections) if sections else "(không có ngữ cảnh bổ sung — trả lời trực tiếp)"
    citations = rag_citations + tool_citations

    logger.info(
        f"Tập hợp ngữ cảnh: {len(docs)} tài liệu, công cụ = {bool(tool_section)}, bộ nhớ = {bool(memory_section)}",
        extra={
            "doc_count": len(docs),
            "citation_count": len(citations)
        }
    )
    return {
        "assembled_context": assembled,
        "citations": citations
    }
