# Manage trace_id in 1 request

import contextvars  # safety for all parallel request
import uuid

_trace_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("trace_id", default="")

# Create new trace_id
def new_trace_id() -> str:
    """Create new trace_id for 1 request, first node (input_guardrail)"""
    trace_id = str(uuid.uuid4())[:8]
    _trace_id_var.set(trace_id)
    return trace_id

# Get trace_id
def get_trace_id() -> str:
    """Get present trace_id. If not, return '-' """
    return _trace_id_var.get() or "-"

# Set trace_id 
def set_trace_id(trace_id: str) -> None:
    """Set trace_id (example after resume, use trace_id from state)"""
    _trace_id_var.set(trace_id)