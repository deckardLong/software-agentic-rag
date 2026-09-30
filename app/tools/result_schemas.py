# Define schemas for validation

from pydantic import BaseModel
from typing import Optional

# Package
class PackageInfoResult(BaseModel):
    name: str
    version: str
    summary: Optional[str] = None
    home_page: Optional[str] = None

# Web
class WebSearchResult(BaseModel):
    results: list

# GitHub
class GitHubSearchResult(BaseModel):
    results: list

# Sandbox
class PythonSandboxResult(BaseModel):
    stdout: str     # output
    stderr: str     # error
    exit_code: int  # 0/1

RESULT_SCHEMAS = {
    "package_info": PackageInfoResult,
    "web_search": WebSearchResult,
    "github_search": GitHubSearchResult,
    "python_sandbox": PythonSandboxResult,
}