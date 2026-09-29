# Define query rewrite schema

from pydantic import BaseModel, Field

class RewrittenQuery(BaseModel):
    """Rewritten query schema"""
    rewritten_query: str = Field(
        description="Truy vấn tìm kiếm tiếng Anh, độc lập, giàu từ khóa kỹ thuật, 1 dòng"
    )