# Define a graph with node, edge and fallback

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.guardrails.input_guardrail import check_input
from app.guardrails.domain_classifier import classify_domain

# Build Graph
def build_graph():
    graph = StateGraph(AgentState)

    # ======== Add Nodes ========
    graph.add_node("input_guardrail", check_input)
    graph.add_node("domain_classifier", classify_domain)

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
            "in_scope": END,
            "out_of_scope": END
        }
    )
    
    return graph.compile()

def get_agent_graph():
    return build_graph()