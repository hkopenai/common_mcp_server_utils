import requests
import json
from typing import Dict, Any, Optional

def fetch_json_data(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[int] = None,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """
    Fetches JSON data from a given URL with optional parameters.

    Args:
        url: The URL to fetch data from.
        params: Optional dictionary of query parameters.

    Returns:
        A dictionary containing the JSON response, or an error message.
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        try:
            return response.json()
        except ValueError as e:
            # If response.json() fails, try manual decoding with BOM stripping
            try:
                content = response.content.decode(encoding).lstrip('\ufeff')
                return json.loads(content)
            except UnicodeDecodeError as decode_err:
                return {
                    "error": (
                        f"UnicodeDecodeError: Failed to decode content with encoding {encoding}: {decode_err}. "
                        "Try a different encoding."
                    )
                }
            except ValueError:
                return {
                    "error": (
                        "Failed to parse JSON response from API. "
                        "The API might have returned non-JSON data or an empty response."
                    )
                }
    except requests.exceptions.HTTPError as http_err:
        return {
            "error": (
                f"HTTP error occurred: {http_err}. "
                f"Status code: {response.status_code}. "
                f"Response: {response.text}"
            )
        }
    except requests.exceptions.ConnectionError as conn_err:
        return {
            "error": f"Connection error occurred: {conn_err}. Please check your network connection."
        }
    except requests.exceptions.Timeout as timeout_err:
        return {
            "error": f"The request timed out: {timeout_err}. Please try again later."
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "error": f"An unexpected error occurred during the request: {req_err}."
        }
