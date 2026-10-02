# Define context assembly config schema

from pydantic import BaseModel

# Define class
class ContextAssemblyConfig(BaseModel):
    max_rag_tokens: int = 2000      # all tokens for RAG docs
    max_tool_result_tokens: int = 800
    max_memory_tokens: int = 600    # short-term + long-term memory