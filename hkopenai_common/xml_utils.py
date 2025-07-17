import requests
import xml.etree.ElementTree as ET
import json


def _xml_to_dict(element):
    """Recursively converts an ElementTree element and its children to a dictionary."""
    result = {}
    for child in element:
        if child.tag not in result:
            result[child.tag] = []
        if len(child) == 0:  # No children, just text
            result[child.tag].append(child.text)
        else:
            result[child.tag].append(_xml_to_dict(child))
    return result


def fetch_xml_from_url(url: str):
    """
    Fetches XML data from a given URL, parses it, and returns it as a JSON-like dictionary.
    Returns a dictionary with an 'error' key if an error occurs.

    Args:
        url (str): The URL to fetch XML from.

    Returns:
        dict: A dictionary representing the parsed XML, or a dictionary with an 'error' key if an error occurs.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        root = ET.fromstring(response.content)
        return {root.tag: _xml_to_dict(root)}
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
