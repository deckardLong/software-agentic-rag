# Define github search tool to search code, repos

import os
import requests
from pydantic import BaseModel, Field

# Define class
class GitHubSearchArgs(BaseModel):
    query: str = Field(description="Từ khóa tìm code/repo, vd 'fastapi dependency injection example'")
    search_type: str = Field(default="repositories", description="'repositories' hoặc 'code'")

# GitHub search
def github_search(query: str, search_type: str = "repositories"):
    # Get headers
    headers = {
        "Accept": "application/vnd.github+json"
    }
    token = os.getenv("GITHUB_TOKEN")

    # Token exists
    if token:
        headers["Authorization"] = f"Bearer {token}"

    # If not exist
    if search_type == "code" and not token:
        return {
            "error": "GitHub code search yêu cầu GITHUB_TOKEN — chưa được cấu hình. Thử search_type='repositories'."
        }

    # Endpoint
    endpoint = f"https://api.github.com/search/{search_type}"
    try:
        # Get response
        resp = requests.get(endpoint, params={
            "q": query,
            "per_page": 5
        }, timeout=10, headers=headers)
        resp.raise_for_status()

        # Items
        items = resp.json().get("items", [])
    except requests.RequestException as e:
        return {
            "error": f"Lỗi khi call GitHub API: {e}"
        }

    # Repos
    if search_type == "repositories":
        results = [
            {
                "repo": i["full_name"],
                "url": i["html_url"],
                "description": i.get("description"),
                "stars": i["stargazers_count"]
            }
            for i in items
        ]
    else:
        results = [
            {
                "path": i["path"],
                "repo": i["repository"]["full_name"],
                "url": i["html_url"]
            }
            for i in items
        ]

    return {
        "results": results
    }