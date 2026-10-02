# Grounding grade schema from LLM answer

from pydantic import BaseModel, Field

class GroundingGrade(BaseModel):
    is_grounded: bool = Field(description="True nếu câu trả lời chỉ dựa trên Ngữ cảnh đã cho, không bịa đặt")
    score: float = Field(description="Điểm faithfulness 0.0-1.0", ge=0.0, le=1.0)
    reason: str = Field(description="Lý do ngắn gọn, nêu rõ claim nào không có căn cứ nếu có")  