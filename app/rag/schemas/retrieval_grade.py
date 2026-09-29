# Define retrieval grade schema

from pydantic import BaseModel, Field

class RetrievalGrade(BaseModel):
    """Retrieval grade schema"""
    relevant_indices: list[int] = Field(
        description="Số thứ tự (bắt đầu từ 1) của các đoạn tài liệu CÓ CHỨA thông tin giúp trả lời "
                    "câu hỏi. Danh sách rỗng nếu không đoạn nào liên quan."
    )