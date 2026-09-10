# Create LLM config objects (Gemini + Ollama)

from pydantic import BaseModel, Field

class OllamaConfig(BaseModel):
    """Ollama LLM configuration (local + development)"""
    provider: str = "ollama"
    model_name: str = "llama3.1:latest"
    base_url: str = "http://localhost:11434"
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = 2048
    timeout_seconds: int = 60

    @property
    def api_endpoint(self) -> str:
        return f"{self.base_url}/api/generate"

class GeminiConfig(BaseModel):
    """Gemini LLM configuration (evaluation + production)"""
    provider: str = "google"
    model_name: str = "gemini-2.0-flash"
    api_key: str
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = 2048
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_backoff_factor: float = 2.0   # retry gets longer if it's timeout => Turn 1: 2s -> Turn 2: 4s -> ...