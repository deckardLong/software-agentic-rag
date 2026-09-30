# Define package info tool to check info of packages

import requests
from pydantic import BaseModel, Field

# Define class
class PackageInfoArgs(BaseModel):
    package_name: str = Field(description="Tên package trên PyPI, vd 'fastapi', 'redis', 'langgraph'")

# Get package info
def get_package_info(package_name: str) -> dict:
    # Get URL
    url = f"https://pypi.org/pypi/{package_name}/json"
    
    try:
        # Get response
        resp = requests.get(url, timeout=10)
        if resp.status_code == 404:
            return {
                "error": f"Không tìm thấy package '{package_name}' trên PyPI"
            } 
        resp.raise_for_status()
        info = resp.json()["info"]
        return {
            "name": info["name"],
            "version": info["version"],
            "summary": info["summary"],
            "home_page": info.get("project_url") or info.get("home_page")
        }
    except requests.RequestException as e:
        return {
            "error": f"Lỗi khi gọi PyPI API: {e}"
        }