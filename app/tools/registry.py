# Registry for all tools

from dataclasses import dataclass
from typing import Callable, Type
from pydantic import BaseModel
from app.tools.implementations.package_info import PackageInfoArgs, get_package_info
from app.tools.implementations.web_search import WebSearchArgs, web_search 
from app.tools.implementations.github_search import GitHubSearchArgs, github_search
from app.tools.implementations.python_sandbox import PythonSandboxArgs, run_python_sandbox
from app.tools.implementations.database_inspect import DatabaseInspectArgs, inspect_database

# Define dataclass
@dataclass
class ToolSpec:
    name: str
    description: str
    args_schema: Type[BaseModel]
    execute: Callable[..., dict]

# Tool registry
TOOL_REGISTRY: dict[str, ToolSpec] = {
    "package_info": ToolSpec(
        name="package_info",
        description="Tra cứu version mới nhất, mô tả, link docs của 1 package Python trên PyPI.",
        args_schema=PackageInfoArgs,
        execute=get_package_info
    ),
    "web_search": ToolSpec(
        name="web_search",
        description="Tìm kiếm web khi câu hỏi cần thông tin ngoài phạm vi corpus đã crawl (tin tức, best practice mới).",
        args_schema=WebSearchArgs,
        execute=web_search
    ),
    "github_search": ToolSpec(
        name="github_search",
        description="Tìm repo/code mẫu liên quan trên GitHub.",
        args_schema=GitHubSearchArgs,
        execute=github_search
    ),
    "python_sandbox": ToolSpec(
        name="python_sandbox",
        description="Chạy thử 1 đoạn code Python ngắn (không I/O, không network) để kiểm chứng hành vi/tính toán.",
        args_schema=PythonSandboxArgs,
        execute=run_python_sandbox
    ),
    "database_inspect": ToolSpec(
        name="database_inspect",
        description="Xem cấu trúc/dữ liệu database của chính hệ thống này (danh sách bảng, cột, "
                    "số dòng, dữ liệu mẫu). CHỈ ĐỌC, không sửa/xóa dữ liệu.",
        args_schema=DatabaseInspectArgs,
        execute=inspect_database
    )
}

# Get tool spec
def get_tool_spec(name: str) -> ToolSpec | None:
    return TOOL_REGISTRY.get(name)

# List tool description
def list_tool_descriptions() -> str:
    return "\n".join(f"- {t.name}: {t.description}" for t in TOOL_REGISTRY.values())