# Define tool guardrail config schema

from pydantic import BaseModel, Field

# Define class
class ToolGuardrailConfig(BaseModel):
    """Permission/risk threshold"""
    sandbox_max_code_length: int = 2000
    database_inspect_blocked_tables: list[str] = Field(
        default_factory=lambda: ["conversation_short_term", "conversation_long_term"]
    )