import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def session_with_retries(
    total=3, backoff_factor=0.5, status_forcelist=(429, 500, 502, 503, 504)
):
    """Requests Session that retries transient failures with exponential backoff."""
    retry = Retry(
        total=total,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    return session
