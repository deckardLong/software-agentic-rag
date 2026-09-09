# Define a graph with node, edge and fallback

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState

# Build Graph
def build_graph():
    graph = StateGraph(AgentState)

    ...
    return graph.compile()
