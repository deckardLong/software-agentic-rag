# Define sandbox for running and checking python code from user

import ast
import subprocess
import sys
import tempfile
from pathlib import Path
from pydantic import BaseModel, Field

# Define blocked modules to avoid injection code
BLOCKED_MODULES = {
    "os", "subprocess", "sys", "socket", "shutil", "ctypes",
    "importlib", "pathlib", "multiprocessing", "threading",
    "requests", "urllib", "http", "ftplib", "telnetlib"
}

TIMEOUT_SECONDS = 5

# Define class
class PythonSandboxArgs(BaseModel):
    code: str = Field(description="Đoạn code Python cần chạy thử, KHÔNG import module I/O hay network")

# Find blocked imports
def _find_blocked_imports(code: str) -> list[str]:
    """Find blocked modules"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"__syntax_error__: {e}"]
    blocked = []

    # Traverse node
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            blocked += [n.name.split(".")[0] for n in node.names if n.name.split(".")[0] in BLOCKED_MODULES]    # get blocked modules
        elif isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            if root in BLOCKED_MODULES:
                blocked.append(root)

    return blocked

# Run Python sandbox
def run_python_sandbox(code: str) -> dict:
    # Get blocked
    blocked = _find_blocked_imports(code)
    if blocked:
        if blocked[0].startswith("__syntax_error__"):
            return {
                "error": f"Code có lỗi cú pháp: {blocked[0].split(':', 1)[1]}"  # syntax error
            }
        return {
            "error": f"Không được phép import: {', '.join(set(blocked))}"       # blocked import
        }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(code)
        script_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )
        return {
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-2000:],
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "error": f"Code chạy quá {TIMEOUT_SECONDS}s, đã bị dừng (có thể là do vòng lặp vô hạn)"
        }
    finally:
        Path(script_path).unlink(missing_ok=True)
    