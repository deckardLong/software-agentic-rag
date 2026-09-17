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
            ...