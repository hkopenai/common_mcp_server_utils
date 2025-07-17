"""Tests for the xml_utils module."""

import xml.etree.ElementTree as ET
from unittest.mock import Mock, patch

import requests

from hkopenai_common.xml_utils import fetch_xml_from_url


class TestXmlUtils:
    """Test cases for xml_utils functions."""

    def setup_method(self):
        """Set up test data for each test method."""
        self.sample_xml_content = """<?xml version="1.0"?>
<data>
    <item>value1</item>
    <item>value2</item>
</data>"""
        self.sample_xml_root = ET.fromstring(self.sample_xml_content)

    @patch("requests.get")
    def test_fetch_xml_from_url_success(self, mock_get):
        """Test successful fetching and parsing of XML data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = self.sample_xml_content.encode("utf-8")
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = "http://example.com/data.xml"
        result = fetch_xml_from_url(url)

        mock_get.assert_called_once_with(url)
        expected_dict = {"data": {"item": ["value1", "value2"]}}
        assert result == expected_dict

    @patch("requests.get")
    def test_fetch_xml_from_url_http_error(self, mock_get):
        """Test fetching XML data when an HTTP error occurs."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Not Found"
        )
        mock_response.text = "Page Not Found"
        mock_get.return_value = mock_response

        url = "http://example.com/nonexistent.xml"
        result = fetch_xml_from_url(url)

        assert "error" in result
        assert "HTTP error occurred" in result["error"]
        assert "Status code: 404" in result["error"]
        assert "Response: Page Not Found" in result["error"]

    @patch("requests.get")
    def test_fetch_xml_from_url_connection_error(self, mock_get):
        """Test fetching XML data when a connection error occurs."""
        mock_get.side_effect = requests.exceptions.ConnectionError(
            "Network unreachable"
        )

        url = "http://example.com/data.xml"
        result = fetch_xml_from_url(url)

        assert "error" in result
        assert "Connection error occurred" in result["error"]

    @patch("requests.get")
    def test_fetch_xml_from_url_timeout(self, mock_get):
        """Test fetching XML data when a timeout occurs."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

        url = "http://example.com/data.xml"
        result = fetch_xml_from_url(url)

        assert "error" in result
        assert "The request timed out" in result["error"]

    @patch("requests.get")
    def test_fetch_xml_from_url_request_exception(self, mock_get):
        """Test fetching XML data when a generic RequestException occurs."""
        mock_get.side_effect = requests.exceptions.RequestException(
            "Something went wrong"
        )

        url = "http://example.com/data.xml"
        result = fetch_xml_from_url(url)

        assert "error" in result
        assert "An unexpected error occurred during the request" in result["error"]

    @patch("requests.get")
    def test_fetch_xml_from_url_parse_error(self, mock_get):
        """Test fetching XML data when XML parsing fails."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<invalid_xml"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        url = "http://example.com/malformed.xml"
        result = fetch_xml_from_url(url)

        assert "error" in result
        assert "Failed to parse XML" in result["error"]

    @patch("requests.get")
    def test_fetch_xml_from_url_unexpected_exception(self, mock_get):
        """Test fetching XML data when an unexpected exception occurs."""
        mock_get.side_effect = Exception("Unknown error")

        url = "http://example.com/data.xml"
        result = fetch_xml_from_url(url)

        assert "error" in result
        assert "An unexpected error occurred: Unknown error" in result["error"]
