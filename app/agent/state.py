# Define a set of data to move around graph (each node)

from typing import TypedDict, Literal, Optional, Any

class AgentState(TypedDict, total=False):
    """State schema for all Agentic RAG pipeline"""

    # ======== Input ========
    user_query: str
    session_id: str
    trace_id: str   # to trace 1 request from end 2 end

    # ======== Input Guardrail & Classifier ========
    input_guardrail_result: Literal["pass", "fail"] 
    input_guardrail_reason: Optional[str]       # explain why it's failed
    domain_in_scope: bool
    domain_out_of_scope_reason: Optional[str]   # explain why it's out of scope

    # ======== Memory ========
    short_term_memory: list[dict]   # query, answer and timestamp, ...
    long_term_memory: list[dict]    # topic, summary and embedding_id, ...

    # ======== Intent Router ========
    route: Literal["rag", "tool", "direct"]
    route_confidence: float     # for debug (0.0 - 1.0)

    # ======== RAG Pipeline ========
    rewritten_query: str
    retrieval_method: Literal["bm25", "vector", "hybrid"]
    retrieved_docs: list[dict]  # [url, title, content, score, ...]
    reranked_docs: list[dict]   # [url, title, content, reranked_score, ...]
    retrieval_grade: Literal["relevant", "irrelevant"]
    retrieval_grade_score: float
    retrieval_retry_count: int

    # ======== Tool Pipeline ========
    selected_tool: Optional[str]    # tool name: "sql_query", "calculator", "code_analyzer"
    tool_params: Optional[dict]     # {"query": "SELECT ..."}
    tool_guardrail_result: Literal["allow", "block"]
    tool_guardrail_block_reason: Optional[str]
    tool_result_raw: Optional[Any]  # result before validation
    tool_validation_result: Literal["valid", "invalid"]
    tool_validation_error: Optional[str]
    sanitized_tool_result: Optional[dict]

    # ======== Context Assembly ========
    assembled_context: str  # combine RAG + Tool + Memory results

    # ======== Generation & Grading ========
    draft_answer: str
    generation_model: str
    generation_tokens_int: int
    generation_tokens_out: int
    grounding_grade: Literal["pass", "fail"]
    grounding_grade_score: float    # faithfulness & hallucination
    grounding_grade_reason: Optional[str]
    generation_retry_count: int
    self_correction_target: Literal["retrieval", "tool", "generation"]  # find exact node to classify bug when answer fail grading
    self_correction_reason: str

    # ======== Output Safety ========
    final_answer: str
    output_guardrail_result: Literal["pass", "block"]
    output_guardrail_block_reason: Optional[str]
    citations: list[dict]   # to know which docs it's retrieved

    # ======== Memory Update ========
    should_save_short_term: bool
    should_save_long_term: bool
    long_term_save_topic: Optional[str] # key for saving long-term memory

    # ======== Observability ========
    step_latencies: dict    # latency for each step
    step_logs: list[str]    # log message for each step
