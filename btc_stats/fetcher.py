from requests.adapters import HTTPAdapter
import requests


def get_json(url):
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=3)
    session.mount('https://', adapter)

    response = session.get(url, timeout=5)
    response.raise_for_status()

    return response.json()
