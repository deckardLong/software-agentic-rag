# Define a graph with node, edge and fallback

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.guardrails.input_guardrail import check_input
from app.guardrails.domain_classifier import classify_domain
from app.agent.nodes.memory_retrieval_node import retrieve_memory
from app.agent.intent_router import route_intent
from app.agent.routing import route_after_retrieval_grade
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
            "direct": END
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
            "relevant": END,
            "retry": "query_rewrite",
            "fallback": "retrieval_fallback" 
        }
    )

    # Step 9: Retrieval Fallback
    graph.add_edge("retrieval_fallback", END)   # fallback

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
            "valid": END,
            "retry": "tool_selection",
            "give_up": "query_rewrite"
        }
    )
    
    return graph.compile()

def get_agent_graph():
    return build_graph()