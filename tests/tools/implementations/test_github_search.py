# Mock test github search

from unittest.mock import MagicMock, patch
from app.tools.implementations.github_search import github_search

class TestGitHubSearch:

    @patch("app.tools.implementations.github_search.requests.get")
    def test_repositories_search_returns_parsed_results(self, mock_get):
        """Return repos with parsed results"""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "items": [{
                "full_name": "tiangolo/fastapi", 
                "html_url": "https://github.com/tiangolo/fastapi",
                "description": "Web framework", 
                "stargazers_count": 70000
            }]
        }
        mock_get.return_value = mock_resp

        result = github_search("fastapi", search_type="repositories")

        assert result["results"][0]["repo"] == "tiangolo/fastapi"

    def test_code_search_without_token_returns_error(self):
        """Test code search"""
        with patch("app.tools.implementations.github_search.os.getenv", return_value=None):
            result = github_search("dependency injection", search_type="code")

        assert "error" in result

    @patch("app.tools.implementations.github_search.requests.get")
    def test_network_error_returns_error_dict(self, mock_get):
        """Test network error"""
        import requests
        mock_get.side_effect = requests.RequestException("rate limited")

        result = github_search("fastapi")

        assert "error" in result