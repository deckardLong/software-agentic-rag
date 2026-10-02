# Mock test web search

from unittest.mock import MagicMock, patch
from app.tools.implementations.web_search import web_search

class TestWebSearch:

    @patch("app.tools.implementations.web_search.DuckDuckGoSearchResults")
    def test_returns_results_list(self, mock_cls):
        """Return list"""
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = [
            {
                "title": "FastAPI docs", 
                "link": "https://fastapi.tiangolo.com"
            }
        ]
        mock_cls.return_value = mock_instance

        result = web_search("FastAPI rate limiting")

        assert "results" in result
        assert len(result["results"]) == 1

    @patch("app.tools.implementations.web_search.DuckDuckGoSearchResults")
    def test_exception_returns_error_dict(self, mock_cls):
        """Return error dict"""
        mock_cls.return_value.invoke.side_effect = Exception("network down")

        result = web_search("bất kỳ query nào")

        assert "error" in result