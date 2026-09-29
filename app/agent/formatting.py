# Convert 2 functions from intent_router.py -> Vietnamese

# Short-term
def format_short_term_context(short_term_memory: list[dict]) -> str:
    """Format short-term context to Vietnamese"""
    if not short_term_memory:
        return "(không có)"
    lines = [f'- Hỏi: "{turn["query"]}" | Đáp: "{turn["answer"][:150]}..."' for turn in short_term_memory]
    return "\n".join(lines)

# Long-term
def format_long_term_context(long_term_memory: list[dict]) -> str:
    """Format long-term context to Vietnamese"""
    if not long_term_memory:
        return "(không có)"
    lines = [f'- {mem["topic"]} (độ liên quan: {mem["similarity"]})' for mem in long_term_memory]
    return "\n".join(lines)
    