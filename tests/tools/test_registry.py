# Test registry

from app.tools.registry import get_tool_spec, list_tool_descriptions, TOOL_REGISTRY

class TestToolRegistry:
    def test_all_five_tools_registered(self):
        """Test 5 tools registry"""
        expected = {
            "package_info", "web_search", "github_search", "python_sandbox", "database_inspect"
        }
        assert set(TOOL_REGISTRY.keys()) == expected

    def test_get_tool_spec_returns_none_for_unknown(self):
        """Return unknown tool"""
        assert get_tool_spec("nonexistent_tool") is None

    def test_get_tool_spec_returns_spec_for_known_tool(self):
        """Return known tool"""
        spec = get_tool_spec("package_info")
        assert spec is not None
        assert spec.name == "package_info"

    def test_list_tool_descriptions_includes_every_tool_name(self):
        """Get all list"""
        descriptions = list_tool_descriptions()
        for name in TOOL_REGISTRY:
            assert name in descriptions