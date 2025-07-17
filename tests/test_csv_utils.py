"""Tests for the csv_utils module."""

from unittest.mock import Mock, patch

import requests

from hkopenai_common.csv_utils import fetch_csv_from_url

# --- Tests for fetch_csv_from_url ---


@patch("requests.get")
def test_fetch_csv_from_url_success(mock_get):
    """Test successful fetching and parsing of CSV data."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"header1,header2\nvalue1,value2\nvalue3,value4"
    mock_get.return_value = mock_response

    url = "http://example.com/data.csv"
    data = fetch_csv_from_url(url)

    mock_get.assert_called_once_with(url)
    assert data == [
        {"header1": "value1", "header2": "value2"},
        {"header1": "value3", "header2": "value4"},
    ]


@patch("requests.get")
def test_fetch_csv_from_url_custom_encoding_delimiter(mock_get):
    """Test fetching CSV data with custom encoding and delimiter."""
    mock_response = Mock()
    mock_response.status_code = 200
    # Simulate UTF-16 LE with BOM and tab delimiter
    mock_response.content = b"\xff\xfeh\x00e\x00a\x00d\x00e\x00r\x001\x00\t\x00h\x00e\x00a\x00d\x00e\x00r\x002\x00\n\x00v\x00a\x00l\x00u\x00e\x001\x00\t\x00v\x00a\x00l\x00u\x00e\x002\x00\n\x00v\x00a\x00l\x00u\x00e\x003\x00\t\x00v\x00a\x00l\x00u\x00e\x004\x00\n\x00"
    mock_get.return_value = mock_response

    url = "http://example.com/data.csv"
    data = fetch_csv_from_url(url, encoding="utf-16-le", delimiter="\t")

    mock_get.assert_called_once_with(url)
    # The BOM character will be part of the first header if not handled by decode
    assert data == [
        {"header1": "value1", "header2": "value2"},
        {"header1": "value3", "header2": "value4"},
    ]


@patch("requests.get")
def test_fetch_csv_from_url_http_error(mock_get):
    """Test fetching CSV data when an HTTP error occurs."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Not Found"
    )
    mock_get.return_value = mock_response

    url = "http://example.com/nonexistent.csv"
    data = fetch_csv_from_url(url)

    assert "error" in data
    assert "HTTP error occurred" in data["error"]
    assert "Status code: 404" in data["error"]


@patch("requests.get")
def test_fetch_csv_from_url_connection_error(mock_get):
    """Test fetching CSV data when a connection error occurs."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

    url = "http://example.com/data.csv"
    data = fetch_csv_from_url(url)

    assert "error" in data
    assert "Connection error occurred" in data["error"]


@patch("requests.get")
def test_fetch_csv_from_url_timeout(mock_get):
    """Test fetching CSV data when a timeout occurs."""
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    url = "http://example.com/data.csv"
    data = fetch_csv_from_url(url)

    assert "error" in data
    assert "The request timed out" in data["error"]


@patch("requests.get")
def test_fetch_csv_from_url_unicode_decode_error(mock_get):
    """Test fetching CSV data when a UnicodeDecodeError occurs."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"invalid_bytes\xfe\xff"  # Invalid UTF-8
    mock_get.return_value = mock_response

    url = "http://example.com/data.csv"
    data = fetch_csv_from_url(url, encoding="utf-8")

    assert "error" in data
    assert "UnicodeDecodeError" in data["error"]


@patch("requests.get")
def test_fetch_csv_from_url_csv_error(mock_get):
    """Test fetching CSV data when a CSV parsing error occurs."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"header1,header2\nvalue1"  # Malformed CSV
    mock_get.return_value = mock_response

    url = "http://example.com/data.csv"
    data = fetch_csv_from_url(url)

    assert "error" in data
    assert "Malformed CSV data" in data["error"]
