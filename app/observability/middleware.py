# Decorator -> Apply all nodes to measure latency

import time
import functools
from typing import Callable
from app.observability.logger import get_logger

logger = get_logger(__name__)

# Define observe node
def observe_node(node_name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(state: dict) -> dict:
            start = time.perf_counter()     # measure performance of code
            result = func(state)
            elapsed_ms = round((time.perf_counter() - start) * 1000, 2)

            # Merge with step_latencies already have in a prev node
            step_latencies = dict(state.get("step_latencies", {}))  # get step_latencies
            step_latencies[node_name] = elapsed_ms                  # add to node
            result["step_latencies"] = step_latencies

            logger.info(f"Node {node_name} đã hoàn thành trong khoảng: {elapsed_ms}ms",
                        extra={
                            "node": node_name,
                            "latency_ms": elapsed_ms 
                        })
            return result
        return wrapper
    return decorator