# Create observability config object

from pydantic import BaseModel
from typing import Optional

class ObservabilityConfig(BaseModel):
    """Logging + tracing"""
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/app.log"
    trace_enabled: bool = True
    metrics_enabled: bool = True