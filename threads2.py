from constants import *
from secrets import *
import requests


def authenticate():
    """
    Authenticate to Threads.

    Returns:
        Tuple containing the Client (for posting tweet) and the API (for v1.1 media upload endpoint)
    """
    resp = requests.