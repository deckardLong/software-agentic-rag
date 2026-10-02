# Mock test for package info

from unittest.mock import MagicMock, patch
from app.tools.implementations.package_info import get_package_info

class TestGetPackageInfo:
    @patch("app.tools.implementations.package_info.requests.get")
    def test_returns_info_for_valid_package(self, mock_get):
        """Return valid package"""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "info": {
                "name": "fastapi", 
                "version": "0.115.0", 
                "summary": "Web framework", 
                "project_url": "https://fastapi.tiangolo.com"
            }
        }
        mock_get.return_value = mock_resp

        result = get_package_info("fastapi")

        assert result["name"] == "fastapi"
        assert result["version"] == "0.115.0"

    @patch("app.tools.implementations.package_info.requests.get")
    def test_404_returns_error(self, mock_get):
        """Test no exist"""
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp

        result = get_package_info("khong-ton-tai-xyz")

        assert "error" in result

    @patch("app.tools.implementations.package_info.requests.get")
    def test_network_error_returns_error_dict_not_exception(self, mock_get):
        """Test network error"""
        import requests
        mock_get.side_effect = requests.RequestException("timeout")

        result = get_package_info("fastapi")

        assert "error" in result