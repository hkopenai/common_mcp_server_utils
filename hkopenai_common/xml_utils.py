import requests
import xml.etree.ElementTree as ET

def fetch_xml_from_url(url: str):
    """
    Fetches XML data from a given URL and parses it.

    Args:
        url (str): The URL to fetch XML from.

    Returns:
        xml.etree.ElementTree.Element: The root element of the parsed XML.

    Raises:
        requests.exceptions.RequestException: If there's an issue fetching the URL.
        xml.etree.ElementTree.ParseError: If there's an issue parsing the XML.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return ET.fromstring(response.content)
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Failed to fetch XML from {url}: {e}")
    except ET.ParseError as e:
        raise ET.ParseError(f"Failed to parse XML from {url}: {e}")
