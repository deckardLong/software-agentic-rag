# Define web search tool to search outside info

from pydantic import BaseModel, Field
from langchain_community.tools import DuckDuckGoSearchResults

# Define class
class WebSearchArgs(BaseModel):
    query: str = Field(description="Từ khóa tìm kiếm, nên viết bằng tiếng Anh để có kết quả tốt hơn")

# Web search
def web_search(query: str) -> dict:
    try:
        tool = DuckDuckGoSearchResults(output_format="list", num_results=5)
        return {
            "results": tool.invoke(query)
        }
    except Exception as e:
        return {
            "error": f"Lỗi khi tìm kiếm web: {e}"
        }