# Define a graph with node, edge and fallback

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.guardrails.input_guardrail import check_input
from app.guardrails.domain_classifier import classify_domain
from app.agent.nodes.memory_retrieval_node import retrieve_memory
from app.agent.intent_router import route_intent
from app.agent.routing import route_after_retrieval_grade, route_after_grounding_grade
from app.rag.query_rewrite import rewrite_query
from app.rag.retriever.hybrid_retriever import hybrid_retrieve
from app.rag.reranker import rerank
from app.rag.retrieval_grader import grade_retrieval
from app.rag.retrieval_fallback import fallback_retrieval
from app.tools.selector import select_tool
from app.tools.tool_guardrail import check_tool
from app.tools.executor import execute_tool
from app.tools.validator import validate_tool_result
from app.tools.sanitizer import sanitize_tool_result
from app.tools.routing import route_after_tool_guardrail, route_after_tool_validation
from app.agent.nodes.direct_answer_node import skip_retrieval_and_tool
from app.agent.nodes.context_assembly_node import assemble_context
from app.agent.nodes.answer_generation_node import generate_answer
from app.agent.nodes.grounding_grader_node import grade_grounding
from app.agent.nodes.self_correction_node import self_correct
from app.guardrails.output_guardrail import check_output
from app.agent.nodes.safe_fallback_node import safe_fallback_answer
from app.agent.nodes.memory_update_node import update_memory
from app.agent.nodes.final_response_node import finalize_response

# Build Graph
def build_graph():
    graph = StateGraph(AgentState)

    # ======== Add Nodes ========
    graph.add_node("input_guardrail", check_input)
    graph.add_node("domain_classifier", classify_domain)
    graph.add_node("memory_retrieval", retrieve_memory)
    graph.add_node("intent_router", route_intent)
    graph.add_node("query_rewrite", rewrite_query)
    graph.add_node("hybrid_retrieval", hybrid_retrieve)
    graph.add_node("reranker", rerank)
    graph.add_node("retrieval_grader", grade_retrieval)
    graph.add_node("retrieval_fallback", fallback_retrieval)
    graph.add_node("tool_selection", select_tool)
    graph.add_node("tool_guardrail", check_tool)
    graph.add_node("tool_execution", execute_tool)
    graph.add_node("tool_validation", validate_tool_result)
    graph.add_node("tool_sanitization", sanitize_tool_result)
    graph.add_node("direct_answer", skip_retrieval_and_tool)
    graph.add_node("context_assembly", assemble_context)
    graph.add_node("answer_generation", generate_answer)
    graph.add_node("grounding_grader", grade_grounding)
    graph.add_node("self_correction", self_correct)
    graph.add_node("output_guardrail", check_output)
    graph.add_node("safe_fallback", safe_fallback_answer)
    graph.add_node("memory_update", update_memory)
    graph.add_node("final_response", finalize_response)

    # ======== Add Edges ========
    graph.set_entry_point("input_guardrail")

    # Step 1: Input Guardrail
    graph.add_conditional_edges(
        "input_guardrail",
        lambda s: "pass" if s.get("input_guardrail_result") == "pass" else "fail",
        {
            "pass": "domain_classifier",
            "fail": END
        }
    )

    # Step 2: Domain Classifier 
    graph.add_conditional_edges(
        "domain_classifier",
        lambda s: "in_scope" if s.get("domain_in_scope") else "out_of_scope",
        {
            "in_scope": "memory_retrieval",
            "out_of_scope": END
        }
    )

    # Step 3: Memory Retrieval
    graph.add_edge("memory_retrieval", "intent_router")

    # Step 4: Intent Router
    graph.add_conditional_edges(
        "intent_router",
        lambda s: s.get("route", "rag"),    # default: RAG
        {
            "rag": "query_rewrite",
            "tool": "tool_selection",
            "direct": "direct_answer"
        }
    )

    # Step 5: Query Rewrite
    graph.add_edge("query_rewrite", "hybrid_retrieval")

    # Step 6: Hybrid Retrieval
    graph.add_edge("hybrid_retrieval", "reranker")

    # Step 7: Reranker
    graph.add_edge("reranker", "retrieval_grader")

    # Step 8: Retrieval Grader
    graph.add_conditional_edges(
        "retrieval_grader",
        route_after_retrieval_grade,
        {
            "relevant": "context_assembly",
            "retry": "query_rewrite",
            "fallback": "retrieval_fallback" 
        }
    )

    # Step 9: Retrieval Fallback
    graph.add_edge("retrieval_fallback", "context_assembly")   # fallback

    # Step 10: Tool Selection
    graph.add_conditional_edges(
        "tool_selection",
        lambda s: "has_tool" if s.get("selected_tool") else "fall_back_to_rag",
        {
            "has_tool": "tool_guardrail",
            "fall_back_to_rag": "query_rewrite"
        }
    )

    # Step 11: Tool Guardrail
    graph.add_conditional_edges(
        "tool_guardrail",
        route_after_tool_guardrail,
        {
            "allow": "tool_execution",
            "block": "query_rewrite"
        }
    )

    # Step 12: Tool Execution
    graph.add_edge("tool_execution", "tool_validation")

    # Step 13: Tool Validation
    graph.add_conditional_edges(
        "tool_validation",
        route_after_tool_validation,
        {
            "valid": "tool_sanitization",
            "retry": "tool_selection",
            "give_up": "query_rewrite"
        }
    )

    # Step 14: Tool Sanitization
    graph.add_edge("tool_sanitization", "context_assembly")

    # Step 15: Direct Answer
    graph.add_edge("direct_answer", "context_assembly")

    # Step 16: Context Assembly
    graph.add_edge("context_assembly", "answer_generation")

    # Step 17: Answer Generation
    graph.add_edge("answer_generation", "grounding_grader")

    # Step 18: Grounding Grader
    graph.add_conditional_edges(
        "grounding_grader",
        route_after_grounding_grade,
        {
            "pass": "output_guardrail",
            "retry": "self_correction",
            "safe_fallback": "safe_fallback"
        }
    )

    # Step 19: Self-Correction
    graph.add_conditional_edges(
        "self_correction",
        lambda s: s["self_correction_target"],
        {
            "retrieval": "query_rewrite",
            "tool": "tool_selection",
            "generation": "answer_generation"
        }
    )

    # Step 20: Output Guardrail
    graph.add_conditional_edges(
        "output_guardrail",
        lambda s: s["output_guardrail_result"],
        {
            "pass": "memory_update",
            "block": "safe_fallback"
        }
    )

    # Step 21: Safe Fallback
    graph.add_edge("safe_fallback", "memory_update")

    # Step 22: Memory Update
    graph.add_edge("memory_update", "final_response")

    # Step 23: Final Response
    graph.add_edge("final_response", END)
    
    return graph.compile()

def get_agent_graph():
    return build_graph()