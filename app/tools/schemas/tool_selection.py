# Define tool selection schema

from pydantic import BaseModel, Field

# Define class
class ToolSelection(BaseModel):
    tool_name: str = Field(description="Tên tool được chọn, khớp CHÍNH XÁC 1 trong các tool đã liệt kê")
    tool_params: dict = Field(description="Tham số truyền cho tool, key-value khớp schema của tool đó")
    reasoning: str = Field(description="Lý do ngắn gọn tại sao chọn tool này")