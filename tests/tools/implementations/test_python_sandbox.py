# Mock test python sandbox

import app.tools.implementations.python_sandbox as sandbox_module
from app.tools.implementations.python_sandbox import run_python_sandbox, _find_blocked_imports

class TestBlockedImports:

    def test_detects_blocked_module(self):
        """Test blocked module"""
        blocked = _find_blocked_imports("import os\nprint(os.getcwd())")
        assert "os" in blocked

    def test_detects_blocked_from_import(self):
        """Test blocked from import"""
        blocked = _find_blocked_imports("from subprocess import run")
        assert "subprocess" in blocked

    def test_allows_safe_modules(self):
        """Test safe modules"""
        blocked = _find_blocked_imports("import math\nprint(math.sqrt(4))")
        assert blocked == []

    def test_syntax_error_detected(self):
        """Test syntax error"""
        blocked = _find_blocked_imports("def foo(:\n  pass")
        assert blocked[0].startswith("__syntax_error__")

class TestRunPythonSandbox:

    def test_runs_simple_code_successfully(self):
        """Test run simple code"""
        result = run_python_sandbox("print(1 + 1)")
        assert result["exit_code"] == 0
        assert "2" in result["stdout"]

    def test_blocked_import_rejected_before_execution(self):
        """Test reject code"""
        result = run_python_sandbox("import os")
        assert "error" in result
        assert "os" in result["error"]

    def test_syntax_error_rejected_before_execution(self):
        """Test syntax error"""
        result = run_python_sandbox("def foo(:\n  pass")
        assert "error" in result

    def test_timeout_is_enforced(self, monkeypatch):
        """Test reduce timeout"""
        monkeypatch.setattr(sandbox_module, "TIMEOUT_SECONDS", 0.2)
        result = run_python_sandbox("while True: pass")
        assert "error" in result
        assert "quá" in result["error"]