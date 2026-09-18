# Create domain classification schema

from pydantic import BaseModel, Field

# Domain Classification
class DomainClassification(BaseModel):
    in_scope: bool = Field(description="True nếu câu hỏi thuộc phạm vi 9 công nghệ hỗ trợ")
    reason: str = Field(description="Lý do ngắn gọn bằng tiếng Việt")