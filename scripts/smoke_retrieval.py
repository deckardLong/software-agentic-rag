# Run smoke test in real data

import sys
from app.observability import setup_logging
from app.rag.query_rewrite import rewrite_query
from app.rag.reranker import rerank
from app.rag.retrieval_grader import grade_retrieval
from app.rag.retriever.hybrid_retriever import hybrid_retrieve

setup_logging()

# Set default queries
DEFAULT_QUERIES = [
    "FastAPI dùng Depends() để làm gì?",
    "Cách tạo một Deployment trong Kubernetes?",
    "Redis pub/sub hoạt động như thế nào?",
    "Làm sao tạo index HNSW trong PostgreSQL?",
    "LangGraph conditional edges dùng để làm gì?",
]

# Run
def run(query: str) -> None:
    state = {
        "user_query": query, 
        "short_term_memory": []
    }
    for node in (rewrite_query, hybrid_retrieve, rerank, grade_retrieval):
        state.update(node(state))

    print(f"\nCâu truy vấn: {query}")
    print(f"Được viết lại (Rewritten): {state['rewritten_query']}")
    print(f"Bộ đánh giá (Grade): {state['retrieval_grade']} (score = {state['retrieval_grade_score']})")
    for doc in state["reranked_docs"]:
        mark = "Đồng ý:" if doc.get("grader_relevant") else "Bác bỏ:"
        print(f"{mark} {doc['rerank_score']:>7} [{doc['source']}] {doc['heading_path'] or doc['title']}")
        print(f"{doc['url']}")


if __name__ == "__main__":
    for q in (sys.argv[1:] or DEFAULT_QUERIES):
        run(q)