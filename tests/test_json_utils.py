import pytest
from unittest.mock import patch, Mock
import requests
from hkopenai_common.json_utils import fetch_json_data

# --- Tests for fetch_json_data ---

@patch('requests.get')
def test_fetch_json_data_success(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(return_value={"key": "value", "number": 123})
    mock_get.return_value = mock_response

    url = "http://example.com/data.json"
    data = fetch_json_data(url)

    mock_get.assert_called_once_with(url, params=None, headers=None, timeout=None)
    assert data == {"key": "value", "number": 123}

@patch('requests.get')
def test_fetch_json_data_with_params_headers_timeout(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(return_value={"status": "ok"})
    mock_get.return_value = mock_response

    url = "http://example.com/api"
    params = {"id": "123"}
    headers = {"Authorization": "Bearer token"}
    timeout = 5
    data = fetch_json_data(url, params=params, headers=headers, timeout=timeout)

    mock_get.assert_called_once_with(url, params=params, headers=headers, timeout=timeout)
    assert data == {"status": "ok"}

@patch('requests.get')
def test_fetch_json_data_custom_encoding(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    # Simulate UTF-16 BE with BOM
    mock_response.json = Mock(return_value={"key": "value"})
    mock_get.return_value = mock_response

    url = "http://example.com/data.json"
    data = fetch_json_data(url, encoding="utf-16-be")

    mock_get.assert_called_once_with(url, params=None, headers=None, timeout=None)
    assert data == {"key": "value"}

@patch('requests.get')
def test_fetch_json_data_http_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Internal Server Error")
    mock_response.text = "Server Error"
    mock_get.return_value = mock_response

    url = "http://example.com/error"
    data = fetch_json_data(url)

    assert "HTTP error occurred" in data["error"]
    assert "Status code: 500" in data["error"]
    assert "Response: Server Error" in data["error"]

@patch('requests.get')
def test_fetch_json_data_connection_error(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError("Network unreachable")

    url = "http://example.com/data.json"
    data = fetch_json_data(url)

    assert "Connection error occurred" in data["error"]

@patch('requests.get')
def test_fetch_json_data_timeout(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    url = "http://example.com/data.json"
    data = fetch_json_data(url)

    assert "The request timed out" in data["error"]

@patch('requests.get')
def test_fetch_json_data_invalid_json(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))
    mock_response.content = b"this is not json"
    mock_get.return_value = mock_response

    url = "http://example.com/invalid.json"
    data = fetch_json_data(url)

    assert "Failed to parse JSON response from API" in data["error"]

@patch('requests.get')
def test_fetch_json_data_unicode_decode_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json = Mock(side_effect=ValueError("Invalid JSON"))
    mock_response.content = b'\xed\xa0\x80' # Invalid UTF-8 sequence
    mock_get.return_value = mock_response

    url = "http://example.com/bad_encoding.json"
    data = fetch_json_data(url, encoding="utf-8")

    assert "UnicodeDecodeError" in data["error"]
