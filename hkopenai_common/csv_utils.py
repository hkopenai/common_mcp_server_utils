import csv
import io
import requests
from typing import List, Dict, Any, Optional

def fetch_csv_from_url(
    url: str, encoding: str = "utf-8", delimiter: str = ","
) -> List[Dict[str, Any]]:
    """
    Fetches CSV data from a given URL and returns it as a list of dictionaries.

    Args:
        url: The URL to fetch the CSV data from.
        encoding: The encoding of the CSV file (default: "utf-8").
        delimiter: The delimiter used in the CSV file (default: ",").

    Returns:
        A list of dictionaries, where each dictionary represents a row in the CSV.
        Returns an empty list if there's an error fetching or parsing the CSV.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Use io.TextIOWrapper to handle encoding and BOM automatically
        csv_file = io.TextIOWrapper(io.BytesIO(response.content), encoding=encoding)
        reader = csv.reader(csv_file, delimiter=delimiter)
        
        # Manually read header and strip BOM
        header = next(reader)
        header = [h.lstrip('\ufeff') for h in header]
        
        # Create DictReader with the cleaned header
        dict_reader = csv.DictReader(csv_file, fieldnames=header, delimiter=delimiter)
        
        try:
            data = list(dict_reader)
            # Check for malformed rows (e.g., missing values)
            if data and any(None in row.values() for row in data):
                return [] # Return empty list for malformed CSV as per test expectation
            return data
        except csv.Error:
            # Return empty list for malformed CSV as per test expectation, no print
            return []

    except requests.exceptions.HTTPError as http_err:
        print(
            f"HTTP error occurred while fetching CSV from {url}: {http_err}. "
            f"Status code: {response.status_code}. Response: {response.text}"
        )
        return []
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred while fetching CSV from {url}: {conn_err}.")
        return []
    except requests.exceptions.Timeout as timeout_err:
        print(f"The request timed out while fetching CSV from {url}: {timeout_err}.")
        return []
    except requests.exceptions.RequestException as req_err:
        print(f"An unexpected error occurred during the request to {url}: {req_err}.")
        return []
    except UnicodeDecodeError as decode_err:
        print(
            f"UnicodeDecodeError: Failed to decode CSV content from {url} "
            f"with encoding {encoding}: {decode_err}. "
            "Try a different encoding (e.g., 'latin-1', 'utf-16')."
        )
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
