# Define schemas intent routing 

from pydantic import BaseModel, Field
from typing import Literal

# Define class
class IntentRouting(BaseModel):
    route: Literal["rag", "tool", "direct"] = Field(
        description="rag: cần tra cứu tài liệu kỹ thuật; tool: cần thực thi hành động cụ thể "
            "(SQL, tính toán, phân tích code); direct: câu hỏi chung chung/chào hỏi, "
            "trả lời được ngay không cần tra cứu hay công cụ gì"
    )
    confidence: float = Field(description="Độ tin cậy để quyết định route, 0.0-1.0", ge=0.0, le=1.0)
    reasoning: str = Field(description="Lý do ngắn gọn bằng tiếng Việt")