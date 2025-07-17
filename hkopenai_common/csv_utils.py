import csv
import io
import requests
from typing import List, Dict, Any, Optional


def fetch_csv_from_url(
    url: str, encoding: str = "utf-8", delimiter: str = ","
) -> List[Dict[str, Any]] | Dict[str, str]:
    """
    Fetches CSV data from a given URL and returns it as a list of dictionaries.
    Returns a dictionary with an 'error' key if an error occurs.

    Args:
        url: The URL to fetch the CSV data from.
        encoding: The encoding of the CSV file (default: "utf-8").
        delimiter: The delimiter used in the CSV file (default: ",").

    Returns:
        A list of dictionaries, where each dictionary represents a row in the CSV,
        or a dictionary with an 'error' key if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Use io.TextIOWrapper to handle encoding and BOM automatically
        csv_file = io.TextIOWrapper(io.BytesIO(response.content), encoding=encoding)
        reader = csv.reader(csv_file, delimiter=delimiter)

        # Manually read header and strip BOM
        header = next(reader)
        header = [h.lstrip("\ufeff") for h in header]

        # Create DictReader with the cleaned header
        dict_reader = csv.DictReader(csv_file, fieldnames=header, delimiter=delimiter)

        try:
            data = list(dict_reader)
            # Check for malformed rows (e.g., missing values)
            if data and any(None in row.values() for row in data):
                return {"error": f"Malformed CSV data from {url}"}
            return data
        except csv.Error as e:
            return {"error": f"Failed to parse CSV from {url}: {e}"}

    except requests.exceptions.HTTPError as http_err:
        return {
            "error": f"HTTP error occurred while fetching CSV from {url}: {http_err}. "
            f"Status code: {response.status_code}. Response: {response.text}"
        }
    except requests.exceptions.ConnectionError as conn_err:
        return {
            "error": f"Connection error occurred while fetching CSV from {url}: {conn_err}."
        }
    except requests.exceptions.Timeout as timeout_err:
        return {
            "error": f"The request timed out while fetching CSV from {url}: {timeout_err}."
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "error": f"An unexpected error occurred during the request to {url}: {req_err}."
        }
    except UnicodeDecodeError as decode_err:
        return {
            "error": f"UnicodeDecodeError: Failed to decode CSV content from {url} "
            f"with encoding {encoding}: {decode_err}. "
            "Try a different encoding (e.g., 'latin-1', 'utf-16')."
        }
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
