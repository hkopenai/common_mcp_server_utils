import requests
import xml.etree.ElementTree as ET


def fetch_xml_from_url(url: str):
    """
    Fetches XML data from a given URL and parses it.
    Returns a dictionary with an 'error' key if an error occurs.

    Args:
        url (str): The URL to fetch XML from.

    Returns:
        xml.etree.ElementTree.Element: The root element of the parsed XML,
        or a dictionary with an 'error' key if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return ET.fromstring(response.content)
    except requests.exceptions.HTTPError as http_err:
        return {
            "error": f"HTTP error occurred while fetching XML from {url}: {http_err}. Status code: {response.status_code}. Response: {response.text}"
        }
    except requests.exceptions.ConnectionError as conn_err:
        return {
            "error": f"Connection error occurred while fetching XML from {url}: {conn_err}."
        }
    except requests.exceptions.Timeout as timeout_err:
        return {
            "error": f"The request timed out while fetching XML from {url}: {timeout_err}."
        }
    except requests.exceptions.RequestException as req_err:
        return {
            "error": f"An unexpected error occurred during the request to {url}: {req_err}."
        }
    except ET.ParseError as e:
        return {"error": f"Failed to parse XML from {url}: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
