import csv
import urllib.request
from typing import List, Dict, Any

def fetch_csv_from_url(url: str) -> List[Dict[str, Any]]:
    """
    Fetches CSV data from a given URL and returns it as a list of dictionaries.

    Args:
        url: The URL to fetch the CSV data from.

    Returns:
        A list of dictionaries, where each dictionary represents a row in the CSV.
        Returns an empty list if there's an error fetching or parsing the CSV.
    """
    try:
        with urllib.request.urlopen(url) as response:
            lines = [l.decode("utf-8") for l in response.readlines()]
            reader = csv.DictReader(lines)
            return list(reader)
    except urllib.error.URLError as e:
        print(f"Error fetching CSV from URL: {e.reason}")
        return []
    except csv.Error as e:
        print(f"Error parsing CSV data: {e}")
        return []
